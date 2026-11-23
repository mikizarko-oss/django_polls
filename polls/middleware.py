
class PollVisitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        poll_id = None

        if request.path.startswith('/polls/'):
            parts = request.path.strip('/').split('/')

            if len(parts) == 2 and parts[1].isdigit():
                poll_id = parts[1]

        if poll_id:
            visits = request.session.get('poll_visits', {})

            visits[poll_id] = visits.get(poll_id, 0) + 1

            request.session['poll_visits'] = visits

        response = self.get_response(request)

        return response
