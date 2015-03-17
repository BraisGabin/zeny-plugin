from rest_framework import permissions


class OnlyOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated()):
            return False
        pk = view.kwargs['pk']
        return pk == 'me' or int(view.kwargs['pk']) == request.user.pk


class BuyOrOnlyOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated()):
            return False
        pk = view.kwargs['pk']
        is_me = pk == 'me' or int(view.kwargs['pk']) == request.user.pk
        if request.method == 'PUT':
            return not is_me
        else:
            return is_me
