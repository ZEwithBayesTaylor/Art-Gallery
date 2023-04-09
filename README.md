### ArtTrackr

PostgreSQL account: yz4429@cs4111-instance

URL: http://34.75.68.224:8111/

Description of implementation versus proposal:
We implemented all the features that we specified in our project proposal.
There is a case-sensitive search function for available artworks within the database, that
returns a table of artworks with titles that include the search term. The table displays the title,
year of creation, and artist of matching artworks, with URLs for the title and artist. Upon clicking 
on the links the user is taken to an information page outlining specific artwork/artist information.
We also implemented our proposed add function for artist and artwork. For any artwork, an associated 
artist is required to be added first, as part of data quality assurance for the database. 

Webpages with interesting database operations:
As the functionality of our application is essentially search and add, the webpages that are associated 
with these two functions are the most interesting. First, in terms of search, the index page of our 
application receives the user input as the query search term, and selects matching artworks from the database
and then displays the results.

Secondly, the next function of add artwork or artist are two separate webpages, which prompt the user
to input the required attribute information, and then parses that input into an insert query on our 
backend database. 

