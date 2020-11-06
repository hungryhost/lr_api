# Backend Changelog
## Contents
- [Authorization Changelog](#authorization-changelog)
- [Profile Changelog](#profile-changelog)
- [Property Changelog](#property-changelog)
### *Authorization Changelog* 
[Last Update 06.11.2020]
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