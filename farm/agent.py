# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import TypedDict, Annotated

from langgraph.graph import END, START, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool, InjectedToolCallId
from common.llm import get_llm
from ioa_observe.sdk.decorators import agent, graph

logger = logging.getLogger("intersight.intersight_data_agent.graph")

class State(TypedDict):
    prompt: str
    error_type: str
    error_message: str
    intersight_response: str

@agent(name="intersight_data_agent")
class IntersightDataAgent:
    def __init__(self):
        self.PRIMARY_NODE = "PrimaryNode"
        self.tools = [self.create_vm]
        self._agent = self.build_graph()

    @graph(name="farm_graph")
    def build_graph(self) -> StateGraph:
        graph_builder = StateGraph(State)
        graph_builder.add_node(self.PRIMARY_NODE, self.primary_node)
        graph_builder.add_edge(START, self.PRIMARY_NODE)
        graph_builder.add_edge(self.PRIMARY_NODE, END)
        return graph_builder.compile()
    
    @tool("create_vm", return_direct=False)
    def create_vm(
        self,
        vm_name_value: str,
        vm_cpu_value: str,
        vm_mem_value: str,
        vm_network_value: str,
        cluster_name_value: str,
        tool_call_id: Annotated[str, InjectedToolCallId] = "",
    ) -> dict:
        """
        Triggers a workflow in Intersight Cloud Orchestrator to provision a new Virtual Machine.
        """
        # TODO: Replace with real ICO API call
        # e.g., requests.post(...); handle auth, errors, etc.
        logger.debug(f"Inside the Tool: create_vm")
        return {
            # "ok": True,
            # "action": "create_vm",
            # "vm_name_value": vm_name_value,
            # "vm_cpu_value": vm_cpu_value,
            # "vm_mem_value": vm_mem_value,
            # "vm_network_value": vm_network_value,
            # "cluster_name_value": cluster_name_value,
            "tool_call_id": tool_call_id,  # echoed so it’s visible in persisted state
            "message": f"Requested VM '{vm_name_value}' in cluster '{cluster_name_value}'.",
        }
    

    async def primary_node(self, state: State):
        # """
        # Generates a coffee flavor profile based on the user's prompt using an LLM.

        # This method takes the current state (which includes a user prompt),
        # sends it to a language model with a specialized system prompt, and returns
        # a brief flavor description based on location and season.

        # If the prompt doesn't contain enough context (e.g., missing location or season),
        # it returns an error response instead of a profile.

        # Args:
        #     state (State): The LangGraph state object containing a 'prompt' key with user input.

        # Returns:
        #     dict: A dictionary with either:
        #         - "intersight_response" (str): A brief tasting profile if valid context was extracted.
        #         - or an "error_type" and "error_message" if the input was insufficient.
        # """
        # session_start()
        user_prompt = state.get("prompt")
        logger.debug(f"Received user prompt: {user_prompt}")

        system_prompt = (
"""
You are the Virtual Machine Management Agent.
Your role is strictly limited to provisioning Virtual Machines.
    - You only handle requests to create Virtual Machines.
    - You accept natural language input describing VM requirements such as CPU, memory, storage, and network.
    - You must translate these requirements into a concrete VM creation action using the create_virtual_machine tool.
    - Do not answer, explain, or discuss topics outside of Virtual Machine provisioning.
    - If the request is not about VM creation, respond with: "This agent only supports Virtual Machine provisioning requests."
"""
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        model = get_llm().bind_tools(self.tools)
        response = model.invoke(messages)
        intersight_response = response.content
        logger.debug(f"LLM response: {intersight_response}")
        if not intersight_response.strip():
            logger.warning("Could not extract valid Intersight Response from the user prompt.")
            return {
                "error_type": "invalid_input",
                "error_message": "Could not confidently extract coffee farm context from user prompt."
            }

        return {"intersight_response": intersight_response}

    async def ainvoke(self, input: str) -> dict:
        """
        Sends a user input string to the agent asynchronously and returns the result.

        Args:
            input (str): A user prompt describing a coffee farm, region, or condition.

        Returns:
            dict: A response dictionary, typically containing either:
                - "intersight_response" with the LLM's generated profile, or
                - An error message if parsing or context extraction failed.
        """
        # build graph if not already built
        if not hasattr(self, '_agent'):
            self._agent = self.build_graph()
        return await self._agent.ainvoke({"prompt": input})