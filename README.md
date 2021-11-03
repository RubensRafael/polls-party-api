# polls-party-api


Welcome to the Polls Party API documentation, to use our services you just need to login to the site with your account (or create one, if you don't already have one) click on the icon at the bottom of the screen and get your api key.

In all requests we need the 'Authentication' header and its value must be: 'Token' + '[whitespace]' + (your api token).

Since we already have a way to create a poll on our website, you don't have to worry about it.

Basically, after creating a poll, you will be able to implement it on your website with just two endpoints. But before we talk about them, let's talk about an important aspect they have, their last url parameter defines the api's data return and they are quite flexible and you can choose which fields you will have as a return, the possibilities are:

- token
- question, 
- options,
- total_votes,
- expires_in,


(separated by '-')

At least one of them is mandatory, if you want to receive everything, just type 'all', the json object is more or less like this, depending on the conditions:




## GET: https://polls-party-api.herokuapp.com/polls/[code]/[params]

The answer to this request is the same as above,
The 'code' is the reference token for the poll, it's accessible from your dashboard,
You don't need to send the auth token to make the request, but then you won't receive the insiths and errors will behave differently.

Errors happen with two conditions:
If the code does not exist,
Or if it expires (the expiration is only when the expiration time is selected in poll creation)

In the first case you will get a 404 error.

In the second the same happens, but you will receive the new token (under the conditions below) if you make the request with your auth token.

When the poll is called by the server, it is checked if that token is expired, if yes he will be updated, after that, the old token no longer exists. The 'new token' (see below) will only be sent in the server response if the current request was responsible for updating the token.

The update also takes place when you enter your dashboard, and the tokens from there will already be updated

We found it easier to use temporary polls on our own site.




## Post: https://polls-party-api.herokuapp.com/polls/vote/[params]

Here you will choose which option to vote, (we do not restrict the number of times a person can vote (this helps the api be used on third party sites, if you want to restrict how many times a person can vote you will have to do it per against itself, in our front-end we use localstorage for example.

The body of the request should look like this:

The first two are mandatory, the third is only if your vote requires a controlfield, with it you'll have a way to identify users with an input in your application (if you have some kind of validation, like regex, we don't care about that , we're just waiting for a string.)

You can access the insights on our website, but if you want to display it in some way, it comes with this structure:
