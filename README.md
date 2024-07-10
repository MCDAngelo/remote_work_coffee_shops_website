# Coffee Shops for Remote Work

This is a website, modelled off of [laptopfriendly.co](https://laptopfriendly.co/london) that shows coffee shops where
it is possible to work remotely for a day.

This website allows users to explore the coffee shops that are already in the database, suggest new locales, and flag if a shop is now closed. 

Future iterations will allow users to leave reviews and will show coffee shops on a map. I looked into using the
[flask_googlemaps](https://github.com/flask-extensions/Flask-GoogleMaps) package, but it is out of date with newer versions of flask and the google maps api.
I'll revisit when the package has been has been updated as per https://github.com/flask-extensions/Flask-GoogleMaps/pull/159).

## Screenshots

![homepage](./images/01-remote_work_cafes-homepage.png)
![homepage with filter](./images/02-remote_work_cafes-homepage_filter.png)
![cafe info page](./images/03-remote_work_cafes-cafe_info.png)
![report closure - unauthenticated user](./images/04-remote_work_cafes-report_closure_unauthenticated.png)
![registration page](./images/05-remote_work_cafes-register.png)
![homepage - authenticated user](./images/07-remote_work_cafes-homepage_authenticated.png)
![login page](./images/09-remote_work_cafes-login.png)
![recommend cafe page](./images/12-remote_work_cafes-recommend_authenticated.png)
![report closure - authanticated user](./images/14-remote_work_cafes-report_closure_authenticated.png)
![admin users page](./images/16-remote_work_cafes-admin_users.png)
![admin cafes page](./images/17-remote_work_cafes-admin_cafes_flagged.png)
![admin delete cafe page](./images/19-remote_work_cafes-admin_delete_cafe.png)
