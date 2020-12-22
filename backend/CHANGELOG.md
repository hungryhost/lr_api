# Backend Changelog
## Contents
- [Authorization Changelog](#authorization-changelog)
- [Users Changelog](#users-changelog)
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
## *Users Changelog* 
[Last Update 11.12.2020]
#### *Introducing new endpoints, avatars and more* *[11.12.2020]*
- Now there are only 3 types of users:
    - internal
        - `staff`
        - `admins`
    - external
        - `users`
<br>
    - Roles like `owner` or `client` are now considered deprecated: any authenticated
    user can create or book a property. <br><br>*Note*: a person can create a property only
    if they have a confirmed main email address. In order to create an organisation, a
    person must confirm both email and phone number.
- Introducing new endpoints:
    - [`GET`, `PATCH`] <br>`api/v1/user/` <br> This endpoint allows access to authenticated user's info.<br>
    This endpoint includes following endpoints:
        - [`GET`, `POST`]<br> `/documents/` - access to a list of documents for the authenticated user.
            - [`PATCH`, `DELETE`]<br> `/<document:id>/` 
        - [`GET`, `POST`] <br>`/phones/` - access to a list of phones for the authenticated user.
            - [`PATCH`, `DELETE`]<br> `/<phone:id/>` 
        - [`GET`, `POST`]<br> `/billing_addresses/` - access to a list of billing addresses for the authenticated user.
            - [`PATCH`, `DELETE`]<br> `/<billing_address:id/>` 
        - [`GET`, `POST`] <br>`/bookings/`- access to a list of bookings of the authenticated user. Bookings for
        the authenticated user are only visible if the user booked a property or the property admin
        booked a property *for the user* and added a valid email of the user. If the email
        has been added and a person decides to register on the service, all the bookings are
        automatically added for that user. All booking will be shown - cancelled or approved.
            - [`GET`, `PATCH`, `DELETE`] <br>`/<booking:id/>` 
        - [`GET`, `POST`]<br> `/emails/` - access to a list of emails for the authenticated user.
            - [`PATCH`, `DELETE`] <br>`/<email:id/>` 
        - [`PUT`, `DELETE`] <br>`/userpic/` - upload or delete user's avatar
        - [`GET`] <br>`/organisations/` - a list of the organisations for the authenticated user.
    - [`GET`] <br>`api/v1/users/` - list of all users.
        - [`GET`]<br> `<user:id>` - get public info for the specific user. 
        - *This endpoint includes other endpoints that are available for admins only. See
        internal documentation for further information.*
    

#### *Minor changes* *[17.11.2020]*
- Moved AccountTypes model into `common` directory.
- Minor changes that do not affect anything outside the directory/app:
    - Minor changes in `permissions.py`. [See the commit](https://git.miem.hse.ru/294/web-294/-/commit/27681a91846fe7eae3f3b2330a2d4b449bf0d215).
    - Minor changes in `views.py`. [See the commit](https://git.miem.hse.ru/294/web-294/-/commit/0f135f6f10a5a2feb4c7ddc12b3d1a8a1099ad98).
    - Minor changes in `admin.py`. [See the commit](https://git.miem.hse.ru/294/web-294/-/commit/2cb059e4284467c2cc39da91afb211764c88829f).
## *Property Changelog* 
[Last Update 14.12.2020]
#### *Introducing image uploading, REST'ful endpoints and bookings* *[14.12.2020]*
- REST API endpoints for the properties now look like that:
    - [`GET`, `POST`]<br> `api/v1/properties/` 
    <br> This endpoint is used for accessing a paginated list of 
    properties *that are publicly available*.<br>
    This endpoint includes following endpoints:
        - [`GET`, `PATCH`, `DELETE`] <br>`/<property:id>/` - allows retrieving, editing and deleting the property. 
            - [`GET`, `POST`] <br> `/owners/` - access to a list of documents for the authenticated user.
                - [`PATCH`, `DELETE`] `/<owner:id>/` 
            - [`GET`, `POST`] <br> `/bookings/` - access to a list of documents for the authenticated user.
                - [`PATCH`, `DELETE`] `/<booking:id>/` 
            - [`GET`, `POST`] <br> `/locks/` - access to a list of documents for the authenticated user.
                - [`PATCH`, `DELETE`] `/<lock:id>/` 
            - [`PUT`, `DELETE`] <br> `/images/` - allows uploading multiple images and bulk delete method.
                - [`DELETE`] `/<image:id>/` 
                - [`PUT`] <br> `/main_image/` - setter for the main image. By default, the main image is the first uploaded image.
- Permission levels have been revised. Now, creators of properties can add other users as admins. Permission levels for admins are listed in the table below. 
<br> 
- Visibility levels have been added for properties. Listed in the table below.
              
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