def frontend_login(request, user):
    """
    Log a user in for the frontend without flushing the session,
    which preserves the admin login state.
    """
    request.session.cycle_key()
    request.session['frontend_user_id'] = user.pk

def frontend_logout(request):
    """
    Log out the frontend user without flushing the session.
    """
    if 'frontend_user_id' in request.session:
        del request.session['frontend_user_id']
        request.session.cycle_key()
