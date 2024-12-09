# crud_fastapi

## To Do
- [x] Add created at and updated at to the users creations
- [ ] (OPTIONAL) Work on this error which raise when I try to register an user "AttributeError: module 'bcrypt' has no attribute '__about__'"
- [x] (Not vulnerable) Test NoSQL injection on the login with Burp Suite
- [ ] Add expire after one usage to the reset password token
- [x] Add status to blog (published and not published) (False = not published)
- [x] Get one and all blog post by published status (When status = True)
- [x] Get all unpublished post by user (user must be authenticated)
- [x] Add function to publish blog post
- [x] Add function to unpublish blog post
- [x] Add timestamp for blog status change (published and unpublished)
- [ ] Change blog hard delete to soft delete
- [ ] Add timestamp for blog delete