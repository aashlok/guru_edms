## Installation

Depends on
* python 3.9
* django 4.2

### On a running server

Step-1:
Visit
```localhost:8000/company/initial-setup/```
to set company Central Document Folder.
A default user admin.<short-code> is created with staff permission for further configuration logins.
Verify folder creation.


Step-2:
Visit
```localhost:8000/company/configuration/```
to access links to create Document Types, Designations and Employees.

Step-3
Visit
```localhost:8000/document/document-types/```
from configuration page to create commonly used document types by the company.

Step-4
Visit
```localhost:8000/company/designations/```
from configuration page to create designation and allow document types created in step-3.

Step-5
Visit
```localhost:8000/company/employees/```
from configuration page to see list of added employees and add employees with designation and shared folder.
Verify creation of employee folder at desired location. 