# Backend Changelog
## Contents
- [Authorization Changelog](#authorization-changelog)
- [Profile Changelog](#profile-changelog)
- [Property Changelog](#property-changelog)
- [General Changelog](#general-changelog)
## *Authorization Changelog* 
[Last Update 17.11.2020]
#### *Minor changes* *[17.11.2020]*
- Minor changes in login and register views. Does not affect anything. 
[See the commit](https://git.miem.hse.ru/294/web-294/-/commit/72e0c869ee0adbed43797f3569490dc0e8b45f41).
#### Added change_password method and minor changes with permissions and Profile model *[10.11.2020]*
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
## *Profile Changelog* 
[Last Update 17.11.2020]
#### *Minor changes* *[17.11.2020]*
- Moved AccountTypes model into `common` directory.
- Minor changes that do not affect anything outside the directory/app:
    - Minor changes in `permissions.py`. [See the commit](https://git.miem.hse.ru/294/web-294/-/commit/27681a91846fe7eae3f3b2330a2d4b449bf0d215).
    - Minor changes in `views.py`. [See the commit](https://git.miem.hse.ru/294/web-294/-/commit/0f135f6f10a5a2feb4c7ddc12b3d1a8a1099ad98).
    - Minor changes in `admin.py`. [See the commit](https://git.miem.hse.ru/294/web-294/-/commit/2cb059e4284467c2cc39da91afb211764c88829f).
## *Property Changelog* 
[Last Update 17.11.2020]
#### *[Refactored serializers](https://git.miem.hse.ru/294/web-294/-/commit/ea251222d1d65339e444c880ba11e92f514744a3)*  *[17.11.2020]*
- In order to make the app's serializers more flexible and easy-to-maintain, 
there is now several separate serializers for POST, GET, DELETE and UPDATE
methods.
#### **IMPORTANT** *[Refactored url paths](https://git.miem.hse.ru/294/web-294/-/commit/b8c928ff7249a0997393d536db08628ff9e7eb54)*  *[17.11.2020]*
- Now most of the actions are separated in their respective urls. For example:
    - `POST` request that created new objects for user's properties now
    must be set to:
    <br>`/api/v1/property/create/`
    - `GET` request that returns a list of all properties must be set to:
    <br>`/api/v1/property/list/`
    - `PUT/PATCH` requests must be set to:
    <br>`/api/v1/property/update/<id>`
    - `DELETE` request must be set to:
    <br>`/api/v1/property/delete/<id>`
- In the upcoming versions the name `property` will be changed to `premises`.
Paths with `property` will be supported until December 2020.
#### *Added validations for price field*  *[17.11.2020]*
- Now `price` field has validation. Price cannot be 0 or less and also
cannot be more than 999999. [See the commit.](https://git.miem.hse.ru/294/web-294/-/commit/40cd27555658dea5c750eb3b072c71bba8de480d)
- `price` field **does not** yet support floating point numbers. 
Will be added soon.
- With new validation in place, new responses are added. [See the commit.](https://git.miem.hse.ru/294/web-294/-/commit/ea251222d1d65339e444c880ba11e92f514744a3)
    - When the `price` field is passed with 0 or less value, following error
    occurs:
        ```json
        {
          "errors": [
            "price : Price cannot be zero or less than a zero"
          ],
          "status_code": 422
        }
        ```
    - When the `price` field is passed with a value bigger than 999999,
    following response is expected:
        ```json
        {
          "errors": [
            "price : Price cannot be that high"
          ],
          "status_code": 422
        }
        ```
- Minor changes with default values. [See the commit.](https://git.miem.hse.ru/294/web-294/-/commit/ea251222d1d65339e444c880ba11e92f514744a3)
   - Now, when a user creates a `property` object without explicitly setting
    `active` status, `active` is set to be
    true by default. 
    - Now, when a user creates a `property` object without an image, a default
    one is used. A url path to that image is returned as usual.
- Minor changes for permissions. [See the commit](https://git.miem.hse.ru/294/web-294/-/commit/35981a1d89bcbd0354e7ad64c1efbb8416ed13fa).
- Minor changes for the `Property` model fields. [See the commit](https://git.miem.hse.ru/294/web-294/-/commit/88e2188207b8b5447945973de273192632dedceb).     
# *General Changelog*
[Last updated 17.11.2020]
#### *Added support for celery and redis* *[17.11.2020.]*
- Now, the celery support has been added. Redis will be used as a broker.
Also, media root has be explicitly set in settings. See the commits:
    - [Changed `settings.py`](https://git.miem.hse.ru/294/web-294/-/commit/6fdf6e89ab7d37c0bc88b1ec4d9e4be7b60810bb)
    - [Changed `__init__.py`](https://git.miem.hse.ru/294/web-294/-/commit/929b3fa14cc224f7c48018fd439adff735018e29)
#### IMPORTANT [*Updated requirements for celery and redis*](https://git.miem.hse.ru/294/web-294/-/commit/6ea74932579e2952aa851ad0eadc48c854529497) *[17.11.2020.]*