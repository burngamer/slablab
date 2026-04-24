You can find the deployed website at slablab.onrender.com
Below are some details about the website's features:

Details about UI/UX:
For the Glassmorphism effect I used the `backdrop-filter: blur(20px)` to make the cards glass-like
There are some custom animations like 'heroGlow' and 'fadeInUP' to make the interface feel responsive
Powered by Google Fonts I used the Outfit and Inter to make the website have a more professional look
For the rarity system there is a css-driven badge system based on the rarity provided with unique color profiles and effects
For a mobile-first approach, since most users will view the site through their mobile device, bootstrap helped me to adjust the UX

Technical details:
The backend is powered by the django framework
The user management (apps.accounts) utilizes a One-to-One relationship to the default Django User model, adding roles (Buyer, Seller, Admin), avatars, and unified address management
Django signals ('post_save') will handle the automatic profile creation upon the registration is completed
Admin-Dashboard -> Although the /admin link is available I created a custom crm-styled admin-dashboard that can only be accessed by the admin after they have signed in and can be found in the profile menu
For the search engine the querying system can filter by price, range, year, grading company and set
The Recommender System:
Although the recommender system is not using any kind of ai or llm to target specific patterns that it can observe through the user behavior
It does track the list of RecentlyViewed and SearchHistory of the customer and it then querries cards that share traits like categories set names or brands with the aforementioned lists
If the recommender does not find these data or the customer is new then it just shows the cards with the higher view count
And before it shows these cards it checks for any duplicate results
Thus giving the feelng of "targeted" recommendations
Integrity Issues:
The OrderItem model is capturing the exact price at the moment of checkout meaning if the seller/admin updates the price the buyer invocice remains the same
By using the on_delete=models.SET_NULL and a redundant empty card field, if the card record is permanently deleted the order history remains the same for the recommender system functionality
Also, the shipping address is copied into 'Orders' to preserve the record exactly as it was shipped
AJAX:
The adding, updating and removing of items occurs in the background
Submitting a review is using an AJAX endpoint to update the card's rating instantly without needing to refresh the page
A unified toggle system is handling the state synchronization across the individual icons 
Search & Filtering
For the querying the system combines some range filters (e.g price) with exact matches (e.g rarity) and partial string matches (e.g name) into a single database querry
The sidebar automatically adapts to show available filters based on the current category or search results

Credentials
Administrator:
Username: admin
Password: admin123
Buyer
Username: thomas5
Password: konstantinos1
Seller
Username: PeterPan01
Password: konstantinos1