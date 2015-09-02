#############
API Reference
#############

********************
"Mainstream" Classes
********************
Most Ministry Platform operations can be performed easiest by using the
classes and objects described in this section. That said, some functions
don't have any further abstractions and must be accessed directly from the
lower-level SOAP function objects.

=================
The Client Object
=================
.. autoclass:: pympl.Client

======================
Request String Objects
======================
.. autoclass:: pympl.RequestString

=============
Table Objects
=============
.. autoclass:: pympl.table.Table
   :members: __call__, record

.. autoclass:: pympl.table.Record
   :members:


**********************
Low(er)-level SOAP API
**********************

=========
Functions
=========

.. autoclass:: pympl.function.FunctionRegistry

.. autoclass:: pympl.function.Function
   :members: __call__, make_request

.. autoclass:: pympl.function.AddRecord
   :members:

.. autoclass:: pympl.function.UpdateRecord
   :members:

.. autoclass:: pympl.function.AuthenticateUser
   :members:

.. autoclass:: pympl.function.GetUserInfo
   :members:

.. autoclass:: pympl.function.AttachFile
   :members:

.. autoclass:: pympl.function.ExecuteStoredProcedure
   :members:


========================================
SOAP Function Request and Response Types
========================================
These objects are used primarily for parsing requests and responses to and
from the Ministry Platform API. Normally, there's no need to interact with
them directly.

========================
Function Request Objects
========================
.. autoclass:: pympl.function.FunctionRequest
   :members:

.. autoclass:: pympl.function.AddRecordRequest
   :members:

.. autoclass:: pympl.function.UpdateRecordRequest
   :members:

.. autoclass:: pympl.function.GetUserInfoRequest
   :members:

.. autoclass:: pympl.function.AttachFileRequest

.. autoclass:: pympl.function.ExecuteStoredProcedureRequest

=========================
Function Response Objects
=========================
.. autoclass:: pympl.function.GetUserInfoResponse
   :members:

.. autoclass:: pympl.function.ExecuteStoredProcedureResponse
   :members:


**********
Exceptions
**********
.. autoclass:: pympl.exc.PymplError
   :show-inheritance:

.. autoclass:: pympl.exc.ServerError
   :show-inheritance:

.. autoclass:: pympl.exc.ResolverError
   :show-inheritance:

.. autoclass:: pympl.exc.FunctionError
   :show-inheritance:

.. autoclass:: pympl.exc.AddRecordError
   :show-inheritance:

.. autoclass:: pympl.exc.UpdateRecordError
   :show-inheritance:

.. autoclass:: pympl.exc.UpdateDefaultImageError
   :show-inheritance:

.. autoclass:: pympl.exc.UpdateUserAccountError
   :show-inheritance:

.. autoclass:: pympl.exc.ResetPasswordError
   :show-inheritance:
