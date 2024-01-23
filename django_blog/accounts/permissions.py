from rest_framework import permissions


"""
generate verified permissions for the project

"""


class IsVerified(permissions.BasePermission):
    message = 'user is not verified.'
    def has_permission(self, request, view):
        return request.user and request.user.is_verified


class IsVerifiedOrReadOnly(permissions.BasePermission):
    message = 'user is not verified.'
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or request.user
            and request.user.is_authenticated
            and request.user.is_verified
        )

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the blog.
        return obj.author == request.user