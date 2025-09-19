# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import TypedDict, Annotated

from langgraph.graph import END, START, StateGraph
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool, InjectedToolCallId
from common.llm import get_llm
from ioa_observe.sdk.decorators import agent, graph
from langgraph.prebuilt import create_react_agent
logger = logging.getLogger("intersight.intersight_data_agent.graph")
import re

class State(TypedDict):
    prompt: str
    error_type: str
    error_message: str
    intersight_response: str

SYSTEM_PROMPT = """You are the Virtual Machine Management Agent.
Your role is strictly limited to provisioning Virtual Machines.

Rules:
- Only handle requests to create Virtual Machines.
- Accept natural language requirements (CPU, memory, storage, network, cluster, VM name).
- Translate them into a concrete VM creation action by calling the `create_vm` tool.
- Do not discuss topics outside VM provisioning.
- If the request is not about VM creation, reply exactly:
  "This agent only supports Virtual Machine provisioning requests."
"""

import subprocess
from intersight.model.workflow_workflow_info import WorkflowWorkflowInfo
from intersight.model.mo_base_mo_relationship import MoBaseMoRelationship
from intersight.model.workflow_workflow_definition_relationship import WorkflowWorkflowDefinitionRelationship
import intersight
from intersight.api import iam_api, workflow_api
import traceback
import os

INTERSIGHT_API_KEY = "68701e3f75646133015b674b/687302317564613201174cc1/68cd97d6756461320130eeda"
INTERSIGHT_SECRET_FILE_PATH = os.getenv(
    "INTERSIGHT_SECRET_FILE_PATH",
    os.path.join(os.path.dirname(__file__), "NSDev01-SecretKey.txt")  # fallback
)

def get_intersight_api_client(api_key_id, api_secret_path, endpoint):
    logger.info("Entering in get_intersight_api_client.")
    logger.info(INTERSIGHT_SECRET_FILE_PATH)
    logger.debug(f"Does the secret file path exists : {os.path.exists(INTERSIGHT_SECRET_FILE_PATH)} ")

    with open(api_secret_path, 'r') as f:
        api_secret_key = f.read()

    # API Key v2 format
    if re.search('BEGIN RSA PRIVATE KEY', api_secret_key):
        signing_algorithm = intersight.signing.ALGORITHM_RSASSA_PKCS1v15
        signing_scheme = intersight.signing.SCHEME_RSA_SHA256
        hash_algorithm = intersight.signing.HASH_SHA256

    # API Key v3 format
    elif re.search('BEGIN EC PRIVATE KEY', api_secret_key):
        signing_algorithm = intersight.signing.ALGORITHM_ECDSA_MODE_DETERMINISTIC_RFC6979
        signing_scheme = intersight.signing.SCHEME_HS2019
        hash_algorithm = intersight.signing.HASH_SHA256
    try:
        configuration = intersight.Configuration(
            host=endpoint,
            signing_info=intersight.signing.HttpSigningConfiguration(
                key_id=api_key_id,
                private_key_path=api_secret_path,
                signing_scheme=signing_scheme,
                signing_algorithm=signing_algorithm,
                hash_algorithm=hash_algorithm,
                signed_headers=[
                    intersight.signing.HEADER_REQUEST_TARGET,
                    intersight.signing.HEADER_HOST,
                    intersight.signing.HEADER_DATE,
                    intersight.signing.HEADER_DIGEST,
                ]
            )
        )
        logger.info(f"Success in get_intersight_api_client")
    except Exception as err:
        logger.exception(
            "Intersight API connection is not successful. Reason: Unauthorized", stack_info=True)
    return intersight.ApiClient(configuration)

def intersight_client_connection():  
    logger.info("Extracting Intersight_client_connection.")
    api_intersight_client = get_intersight_api_client(INTERSIGHT_API_KEY, INTERSIGHT_SECRET_FILE_PATH, endpoint="https://www.intersight.com")
    logger.debug(f"API Client in intersight_client_connection: {api_intersight_client}")
    # Perform a lightweight test to validate credentials
    try:
        account_api = iam_api.IamApi(api_intersight_client)
        account_info = account_api.get_iam_account_list(top=1)
        logger.info("✅ Intersight client authentication successful.")
    except intersight.exceptions.ApiException as e:
        if e.status == 401:
            logger.error("❌ Authentication failed: Unauthorized (401). Check API key and secret.")
        elif e.status == 403:
            logger.error("❌ Access forbidden (403). API key may lack necessary permissions.")
        elif e.status == 400:
            logger.error("❌ Bad request (400). Possibly malformed auth headers or key.")
        else:
            logger.error(f"❌ API exception during client validation: {e}")
    except Exception as ex:
        logger.error(f"❌ Unexpected error during client validation: {traceback.format_exc()}")

    return api_intersight_client

def triggerVMIcoWorkflow(vm_name_value, vm_cpu_value, vm_mem_value, vm_network_value, cluster_name_value):
        logger.info("______Getting inside triggerVMIcoWorkflow...")
        """Trigger the ICO Workflow in Intersight to create a VM."""
        api_intersight_client = intersight_client_connection()

        mo = WorkflowWorkflowInfo(
            action="Start",
            associated_object=MoBaseMoRelationship(
                class_id="mo.MoRef",
                moid="68701e436972653101590c8e",
                object_type="organization.Organization"
            ),
            input={
                 "Cluster": f"/Vzure-Frisco/host/{cluster_name_value}",
                 "VM_Name": vm_name_value, 
                 "CPU": int(vm_cpu_value),
                 "Memory": int(vm_mem_value),
                 "Network": vm_network_value
               }, 
            name="ProvisionNewVM", 
            workflow_definition=WorkflowWorkflowDefinitionRelationship(
                class_id="mo.MoRef",
                moid="687089ff696f6e32017400d3",
                object_type="workflow.WorkflowDefinition"
            )
        )
        try:
            logger.info(f"Name in the MO input: {mo.input['VM_Name']}")
            logger.info(f"Entire MO: {mo}")
            api_instance = workflow_api.WorkflowApi(api_intersight_client)
            workflow = api_instance.create_workflow_workflow_info(mo)
            logger.info(f"Workflow: {workflow}")
            if workflow.get('WorkflowStatus') == 'Waiting' or workflow.get('workflow_status') == 'Waiting':
                logger.info("Workflow is in 'Waiting' state. Initiating background monitoring...")

                # Start monitoring in a background process
                # script_path = os.path.join(settings.BASE_DIR, 'advensisapp', 'dao', 'TriggerWfMonitor.py')
                # subprocess.Popen([
                #     "python3", script_path, 
                #     INTERSIGHT_API_KEY, 
                #     INTERSIGHT_SECRET_FILE_PATH, 
                #     workflow.get('moid')
                # ])

                # logger.info(f"Monitoring started for workflow MOID: {workflow.get('moid')} in the background.")
                logger.info("______Getting outside triggerVMIcoWorkflow...")
                return None, {"message": "Workflow created successfully and is in 'Waiting' status."}
            else:
                logger.info(f"Workflow created but is in unexpected status: {workflow.get('WorkflowStatus')}")
                logger.info("______Getting outside triggerVMIcoWorkflow...")
                return None, {"message": f"Workflow created, but current status is: {workflow.get('WorkflowStatus')}"}
                
        except intersight.OpenApiException as e:
            logger.info(e)

# --- Tool implementation -------------------------------------------------
@tool("create_vm", return_direct=False)
def create_vm(
    vm_name_value: str,
    vm_cpu_value: str,
    vm_mem_value: str,
    vm_network_value: str,
    cluster_name_value: str,
) -> dict:
    """
    Triggers a workflow in Intersight Cloud Orchestrator to provision a new Virtual Machine.
    (Replace the placeholder logic with a real ICO API call + auth + error handling.)
    """
    try:
        logger.info(
            "Triggering Create VM Workflow: [create_vm] name=%s cpu=%s mem=%s net=%s cluster=%s",
            vm_name_value, vm_cpu_value, vm_mem_value, vm_network_value, cluster_name_value
        )
        
        # Attempt to trigger ICO workflow
        triggerVMIcoWorkflow(
            vm_name_value=vm_name_value,
            vm_cpu_value=vm_cpu_value,
            vm_mem_value=vm_mem_value,
            vm_network_value=vm_network_value,
            cluster_name_value=cluster_name_value
        )
        
        logger.info("Successfully triggered Create VM workflow for VM=%s", vm_name_value)

        return {
            "status": "success",
            "message": (
                f"Requested successfully with VM '{vm_name_value}' "
                f"in cluster '{cluster_name_value}' "
                f"with CPU={vm_cpu_value}, MEM={vm_mem_value}, NET={vm_network_value}."
            ),
        }

    except Exception as e:
        logger.error("Error triggering Create VM workflow: %s", str(e), exc_info=True)
        return {
            "status": "error",
            "message": f"Failed to trigger VM creation for '{vm_name_value}': {str(e)}",
        }

@agent(name="intersight_data_agent")
class IntersightDataAgent:
    def __init__(self):
        logger.info(f"AGent in Virtual Machine Agent")
        self.tools = [create_vm]
        self._agent = self.build_graph()
    
    
    @graph(name="farm_graph")
    def build_graph(self) -> StateGraph:
        """
        Build a prebuilt ReAct agent graph:
        - Injects a system prompt (state_modifier)
        - Registers tools
        - Returns a compiled runnable you can .invoke()/.ainvoke()
        """
        logger.info(f"Building the graph for VM AGent with Tool for Intersight")
        llm = get_llm()
        react = create_react_agent(
            model=llm,
            tools=self.tools,
            prompt=SYSTEM_PROMPT,
            # Ensures the system prompt is always present:
            # state_modifier=SystemMessage(content=SYSTEM_PROMPT),
            # Optional: cap steps to 2 (think -> tool -> final)
            # max_steps=2,
            name="vm_create_agent",
        )
        logger.info(f"Response from create_react_agent: {react}")
        return react

    
    async def ainvoke(self, input: str) -> dict:
        """
        Send a prompt to the ReAct agent. The agent will reason and call `create_vm` when appropriate.
        Returns a dict with "intersight_response" for your app.
        """

        state = await self._agent.ainvoke({"messages": [HumanMessage(content=input)]})
        logger.info(f"State after invoking: {state}")
        msgs = state.get("messages", [])
        last = msgs[-1] if msgs else None
        content = getattr(last, "content", "") if last else ""
        logger.info(f"Content from the invoke: {content}")

        if not content:
            # Fallback when nothing is returned
            content = "This agent only supports Virtual Machine provisioning requests."

        return {"intersight_response": content}