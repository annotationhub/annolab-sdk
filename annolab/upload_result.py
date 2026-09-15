from typing import Any, Dict, Optional

from annolab.workflow_execution import WorkflowExecution


class UploadResult:
  """
  The result of uploading a pdf source (e.g. LandAbstract.upload_file).

  Attributes:
    pending_source: dict  The pending source record created by the upload.
    execution:      Optional[WorkflowExecution]
                          The workflow execution started by the upload, or
                          None when the upload did not start a workflow.
    execution_id:   Optional[int]
                          The id of the started workflow execution, if any.
    raw:            dict  The raw response body from the create pdf source call.

  For backwards compatibility this object also unpacks as a
  (pending_source, execution) tuple.
  """

  def __init__(
    self,
    pending_source: Optional[Dict[str, Any]],
    execution: Optional[WorkflowExecution] = None,
    raw: Optional[Dict[str, Any]] = None,
  ):
    self.pending_source = pending_source
    self.execution = execution
    self.raw = raw or {}


  @property
  def execution_id(self) -> Optional[int]:
    if self.execution is not None:
      return self.execution.id

    return self.raw.get('executionId')


  @property
  def has_execution(self) -> bool:
    """True when the upload started a workflow execution."""
    return self.execution is not None


  @property
  def pending_source_id(self) -> Optional[int]:
    if self.pending_source is None:
      return None

    return self.pending_source.get('id')


  def wait_until_complete(self, timeout: float = 3600, poll_rate: float = None):
    """
      Wait for the started workflow execution (if any) to reach a terminal
      status. A no-op when no workflow was started. Returns the execution,
      or None if there is none.
    """
    if self.execution is None:
      return None

    return self.execution.wait_until_complete(timeout=timeout, poll_rate=poll_rate)


  @staticmethod
  def create_from_response_json(resp_json: Dict[str, Any], api_helper):
    execution = None
    execution_id = resp_json.get('executionId')

    if execution_id:
      execution = WorkflowExecution.get(api_helper, execution_id)

    return UploadResult(
      pending_source=resp_json.get('pendingSource'),
      execution=execution,
      raw=resp_json,
    )


  # Backwards compatibility: `pending_source, execution = abstract.upload_file(...)`
  def __iter__(self):
    yield self.pending_source
    yield self.execution


  def __getitem__(self, index: int):
    return (self.pending_source, self.execution)[index]


  def __len__(self):
    return 2


  def __repr__(self):
    status = self.execution.status if self.execution is not None else None
    return (
      f'UploadResult(pending_source_id={self.pending_source_id!r}, '
      f'execution_id={self.execution_id!r}, execution_status={status!r})'
    )
