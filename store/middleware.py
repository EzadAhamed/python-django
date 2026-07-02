from django.contrib.auth.models import User, AnonymousUser
from django.utils.functional import SimpleLazyObject

def get_frontend_user(request):
    if not hasattr(request, '_cached_frontend_user'):
        frontend_user_id = request.session.get('frontend_user_id')
        if frontend_user_id:
            try:
                request._cached_frontend_user = User.objects.get(pk=frontend_user_id)
            except User.DoesNotExist:
                request._cached_frontend_user = AnonymousUser()
        else:
            request._cached_frontend_user = AnonymousUser()
    return request._cached_frontend_user

class DualAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Back up frontend auth state in case an admin action flushes the session
        cached_frontend_user_id = request.session.get('frontend_user_id')
        is_admin_path = request.path.startswith('/admin/')

        # 2. For paths outside of /admin/, override request.user with our frontend session key
        if not is_admin_path:
            request.user = SimpleLazyObject(lambda: get_frontend_user(request))
            
        # 3. Process the view (an admin login/logout will flush the session!)
        response = self.get_response(request)
        
        # 4. If this was an admin action that destroyed the session, restore the frontend auth state
        if is_admin_path and cached_frontend_user_id:
            if 'frontend_user_id' not in request.session:
                request.session['frontend_user_id'] = cached_frontend_user_id
                
        return response
