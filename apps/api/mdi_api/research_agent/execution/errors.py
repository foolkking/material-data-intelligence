class ExecutionDispatchError(ValueError):
    pass


class ExecutionPlanNotReady(ExecutionDispatchError):
    pass


class ExecutionPlanIdentityMismatch(ExecutionDispatchError):
    pass


class ExecutionSourceUnavailable(ExecutionDispatchError):
    pass


class ExecutionQueuePublishFailed(ExecutionDispatchError):
    pass


class ExecutionSummaryConflict(ExecutionDispatchError):
    pass


class ExecutionProgressProjectionFailed(ExecutionDispatchError):
    pass


class ExecutionCancelRequestFailed(ExecutionDispatchError):
    pass
