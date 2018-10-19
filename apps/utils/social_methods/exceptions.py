"""
This module contains our custom Exception for the vk lib wrapper

Notes:
    There are several questionable moments about exception handling in vk lib
    that's why some social_methods starts with vk_* contain additional info
    about this kind of problems. VK library was abandoned 07.2017, but it still
    provides friendly API to start working with.
"""


class VKWrapperException(Exception):
    """ Base exception for all VK exceptions """


class VKAPIParseFail(VKWrapperException):
    """ Risen when it's not possible to receive an answer from VK side """


class VKLinkIsDefective(VKWrapperException):
    """ Risen when user link is defective and cannot be used in VK API """


class VKIncorrectCredentials(VKWrapperException):
    """ Used when user data is wrong. Could happen only on our servers if
        DB store incorrect user data.
    """


class VKIncorrectDataInput(VKWrapperException):
    """ Used in serializers if input data is incorrect """
