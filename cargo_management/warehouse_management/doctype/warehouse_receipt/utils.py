from .constant import Status

class WarehouseStateMachine:
    def __init__(self, status=Status.OPEN):
        self.state = status

    def _allowed_transition(self, value, allowed_statuses: list) -> bool:
        """
        Check if the transition to the given status is allowed.
        
        :param value: The status to transition to.
        :param allowed_statuses: List of statuses to which transitions are allowed.
        :return: True if the transition is allowed, False otherwise.
        """
        if value in allowed_statuses:
            self.state = value
            return True
        else:
            return False

    def transition(self, event: Status) -> bool:
        """
        Handle the transition based on the current state and event.

        :param event: The status to transition to.
        :return: True if the transition is successful, False otherwise.
        """
        match self.state:
            case Status.AWAITING_DEPARTURE:
                return self._allowed_transition(event, [
                    Status.IN_TRANSIT, 
                    Status.SORTING
                ])
            case Status.IN_TRANSIT:
                return self._allowed_transition(event, [
                    Status.SORTING
                ])
            case Status.OPEN:
                return self._allowed_transition(event, [
                    Status.FINISHED, 
                    Status.SORTING
                ])
            case Status.SORTING:
                return self._allowed_transition(event, [
                    Status.FINISHED
                ])
            case Status.FINISHED:
                # Finished status is the final state, no transitions allowed.
                return False
            case _:
                return False
