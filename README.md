# CS50 Final Project - Galaxy SHOP

The final project named "**Galaxy**"  is  a simple e-commerce  shopping platform . The  system  keep all information about users, products, users' carts and the orders. It is controlled by an admin. The admin had to add categories, products, and the relative information. He also manage these on editing, deleting, and delivering the users' orders. The implementation on building this platform is fairly simple. The concepts and technologies used are beginner-friendly and can be easily understand.



Technologies used:

- python3
- flask
- jinja template engine
- sqlite3
- cs50 library 
- werkzeug
- HTML5, CSS3, JavaScript
- Flexbox (modern CSS technique for responsive)
- Bootstrap (CSS framework)



## How the platform works?

Login process(authentication) is not required to view the products. But to add products the shopping cart, order the items on shop, the users must login the **Galaxy SHOP**. 

**Registration** is quick and easy. A user need 

- name
- email
- password(at least 6 characters) 
- reconfirm password

The system check the above requirements and if no issue, hash the password and save the information to the database. The user can login the **SHOP** using email and password and the **session**  is used to store user's id until the user logout.   

#### User Views

- **Home** - presents the users the types of items available, the **New Arrival** products and the other items.   
- **Categories** - the users can see all of the items on **SHOP**  and also filter by categories. The detail of the specific product is done by clicking the image of each product item.
- **Detail product** -  *add to cart* function is in this page. The user can add items no more than the current stocks to the cart. The system save the items and current user's id into the database.
- **About** - a brief information about **Galaxy** how started, current condition, founders and team, customer reviews and so on.
- **Contact** -  A contact form to connect the *Team*
- **Cart**  - cart items of the current users, total bill, a form to order these cart items.
- **Order** - the orders of current users sorted by date in descending order.



#### Admin Views

- **Product Management** - show the products of **SHOP**. The admin can add, edit, delete these items on this page.

-  **Category Management****  -   show the categories of **SHOP**. The admin can add, edit, delete these items on this page.

- **Order Management**** - All of the customers' orders are shown sorted by received date in descending order. ***Mark as delivered*** button is to inform the user that the order is delivered at with a date the  admin mark that order.

  

#### Databse

Before saving into the database, the system check the requirements submitted from the form. Authentication is required for every database process. Database stores all the information of users, categories, products, users' cart and orders. The table, like products, has category id to relate the specific category and in this case, it uses foreign key to reference  the id of categories table.

Here  is **ER diagram** of the system.

![ER](https://user-images.githubusercontent.com/44525618/97115125-3c6cf580-1723-11eb-801a-9d450c690195.png)



#### Further improvements

- Email notification in ordering process.
- Real time system for the whole platform
- **Chat**  to ask about the item detail

