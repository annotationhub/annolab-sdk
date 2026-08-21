from typing import Any, Dict, List, Optional

from polling2 import poll

from annolab import endpoints
from annolab.api_helper import ApiHelper


TERMINAL_WORKFLOW_STATUSES = {
  'Completed',
  'Error',
  'PartialError',
  'Cancelled',
}


class WorkflowExecutionTask:
  """
  A single task within a workflow execution.
  """

  def __init__(
    self,
    id: int,
    task_type: str,
    task_name: str,
    status: str,
    start_time: Optional[str],
    end_time: Optional[str],
  ):
    self.id = id
    self.task_type = task_type
    self.task_name = task_name
    self.status = status
    self.start_time = start_time
    self.end_time = end_time


  @staticmethod
  def create_from_response_json(resp_json: Dict):
    return WorkflowExecutionTask(
      id=resp_json['id'],
      task_type=resp_json.get('taskType'),
      task_name=resp_json.get('taskName'),
      status=resp_json.get('status'),
      start_time=resp_json.get('startTime'),
      end_time=resp_json.get('endTime'),
    )


class WorkflowExecution:
  """
  A workflow execution returned by GET /v1/workflow/execution/:id.
  """

  min_poll_rate = 5
  default_poll_rate = 15

  def __init__(
    self,
    id: int,
    workflow: Optional[str],
    status: str,
    project_id: int,
    start_time: Optional[str],
    end_time: Optional[str],
    created_by: Optional[Dict[str, Any]],
    created_at: str,
    source_ids: List[int],
    tasks: List[WorkflowExecutionTask],
    api_helper: ApiHelper = None,
  ):
    self.id = id
    self.workflow = workflow
    self.status = status
    self.project_id = project_id
    self.start_time = start_time
    self.end_time = end_time
    self.created_by = created_by
    self.created_at = created_at
    self.source_ids = source_ids or []
    self.tasks = tasks or []
    self.__api = api_helper


  @staticmethod
  def create_from_response_json(resp_json: Dict, api_helper: ApiHelper):
    execution = WorkflowExecution(
      id=resp_json['id'],
      workflow=resp_json.get('workflow'),
      status=resp_json.get('status'),
      project_id=resp_json.get('projectId'),
      start_time=resp_json.get('startTime'),
      end_time=resp_json.get('endTime'),
      created_by=resp_json.get('createdBy'),
      created_at=resp_json.get('createdAt'),
      source_ids=resp_json.get('sourceIds') or [],
      tasks=[],
      api_helper=api_helper,
    )
    execution.tasks = [
      WorkflowExecutionTask.create_from_response_json(task)
      for task in (resp_json.get('tasks') or [])
    ]
    return execution


  @staticmethod
  def get(api_helper: ApiHelper, execution_id: int):
    res = api_helper.get_request(endpoints.Workflow.get_execution(execution_id))
    return WorkflowExecution.create_from_response_json(res.json(), api_helper)


  def refresh_status(self):
    """
      Query the workflow execution endpoint and refresh this object's
      status, tasks, and other top-level fields.
    """
    if self.__api is None:
      raise Exception('This WorkflowExecution is not connected to the API')

    res = self.__api.get_request(endpoints.Workflow.get_execution(self.id))
    refreshed = WorkflowExecution.create_from_response_json(res.json(), self.__api)

    self.workflow = refreshed.workflow
    self.status = refreshed.status
    self.project_id = refreshed.project_id
    self.start_time = refreshed.start_time
    self.end_time = refreshed.end_time
    self.created_by = refreshed.created_by
    self.created_at = refreshed.created_at
    self.source_ids = refreshed.source_ids
    self.tasks = refreshed.tasks

    return self.status


  def wait_until_complete(self, timeout: float = 3600, poll_rate: float = None):
    """
      Poll the workflow execution until it reaches a terminal status:
      Completed, Error, PartialError, or Cancelled.

      poll_rate is the number of seconds between status checks. It defaults
      to 15 seconds and cannot be less than 5 seconds.
    """
    step = max(self.min_poll_rate, poll_rate if poll_rate is not None else self.default_poll_rate)

    self.refresh_status()

    if self.status not in TERMINAL_WORKFLOW_STATUSES:
      poll(
        lambda: self.refresh_status() in TERMINAL_WORKFLOW_STATUSES,
        step=step,
        timeout=timeout
      )

    return self
