# Backend Changelog
## Contents
- [Authorization Changelog](#authorization-changelog)
- [Profile Changelog](#profile-changelog)
- [Property Changelog](#property-changelog)
### *Authorization Changelog* 
[Last Update 10.11.2020]
#### Added logout and logout_all methods *[10.11.2020]*
- Added method for changing user's password. `api/v1/profile/change_password/<profile_id>/`
<br>Uses Django User model for it is the one used for authentication.
Requires authorization passed with PUT request. 
  - This endpoint has `400` and `403` error codes (see docs) or `422` when
  there's something wrong with given passwords.
  - When the request has been processed, `204 No content` code is returned 
  with the empty body.
  - Example request with a given token would look like the following snippet:
   ```json
    {
      "old_password": "qwerty1234", 
      "password": "qwerty1235",
      "password2": "qwerty1235"
    }
    ```
    - The new password in fields `password` and `password2` must be the same and 
    and cannot be the same as the old password (otherwise `422` error code).  
- Added permissions for password change (see __*/userAccount/permissions.py*__).
- Minor changes Profile model (now a primary key is also a foreign key).

#### Added logout and logout_all methods *[06.11.2020]*
- Added logout method. `api/v1/auth/logout/` <br>Now, when a POST request from authenticated user is sent 
to `api/v1/auth/logout/` with a refresh token in request body and with access 
token as authorization, a refresh token for that user is added to blacklist. 
   - Also, for that purpose a lifetime of access token is now 5 minutes.
   - Refresh token now lasts one (1) day.
   - Example of request:
    ```json
    {
      "refresh": "<refresh token>"
    }
    ```
  - Response: 205 Reset content (may be changed in the future)
- Added logout_add method. `api/v1/auth/logoutall/` <br>Does the same action as logout but for all tokens
associated with the user. Same request and response bodies.
#### Updated login response *[04.11.2020]*
- Authorization request updated in accordance with the documentation
### *Profile Changelog* 
[Last Update 04.11.2020]
### *Property Changelog* 
[Last Update 04.11.2020]