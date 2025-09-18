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
        logger.info(f"AGent in Virtual Machine Agent")
        self.PRIMARY_NODE = "PrimaryNode"
        self.tools = [self.create_vm]
        self._agent = self.build_graph()

    @graph(name="farm_graph")
    def build_graph(self) -> StateGraph:
        logger.info(f"Building the Graph for Virtual Machine Agent")
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
        Create a new Virtual Machine.

        This tool simulates the creation of a Virtual Machine in a target cluster.
        In production, replace the placeholder implementation with an actual 
        ICO API call (e.g., via `requests.post(...)`) including authentication 
        and error handling.

        Args:
            vm_name_value (str): Name of the virtual machine to be created.
            vm_cpu_value (str): Number of CPUs to allocate for the VM.
            vm_mem_value (str): Amount of memory to allocate (e.g., '8GB').
            vm_network_value (str): Network configuration or port group to attach.
            cluster_name_value (str): Target cluster where the VM should be created.
            tool_call_id (str, optional): Identifier for tracing/logging tool usage.

        Returns:
            dict: A structured response with the tool call ID and a confirmation message.
        """
        logger.info(
            f"[create_vm] Request received for VM '{vm_name_value}' "
            f"(CPU={vm_cpu_value}, MEM={vm_mem_value}, NET={vm_network_value}) "
            f"in cluster '{cluster_name_value}'."
        )

        return {
            "tool_call_id": tool_call_id,  # Echoed back for state persistence/tracing
            "message": (
                f"Requested creation of VM '{vm_name_value}' in cluster '{cluster_name_value}' "
                f"with {vm_cpu_value} CPU, {vm_mem_value} memory, and network '{vm_network_value}'."
            ),
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
        logger.debug(f"Primary Node: Received user prompt: {user_prompt}")

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
        logger.info(f"Messages while invoking the llm: {messages}")
        model = get_llm().bind_tools(self.tools)
        response = model.invoke(messages)
        logger.info(f"Raw Response from LLM: {response}")
        intersight_response = response.content
        logger.debug(f"Primary Node: LLM response: {intersight_response}")
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