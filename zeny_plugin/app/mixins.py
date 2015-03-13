from rest_framework import views
from rest_framework.exceptions import PermissionDenied


class UserMe(views.APIView):
    def initial(self, request, *args, **kwargs):
        super(UserMe, self).initial(request, *args, **kwargs)

        pk = self.kwargs['pk']
        if pk == 'me':
            self.kwargs['pk'] = self.request.user.pk
        elif self.request.user.pk != int(pk):
            raise PermissionDenied()
