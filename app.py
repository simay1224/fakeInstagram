import pymysql.cursors
from flask import Flask, redirect, render_template, request, session, url_for, flash

app = Flask(__name__)

# Config mysql
conn = pymysql.connect(host = 'localhost', 
                    user= 'root', 
                    password= 'password123',
                    db='beta',
                    cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/register')
def register():
    return  render_template('register.html')

@app.route('/login')
def login():
    return  render_template('login.html')

@app.route('/makeTagRequests')
def makeTagRequests():
    return  render_template('makeTagRequests.html')

@app.route('/makeFollowRequests')
def makeFollowRequests():
    return  render_template('makeFollowRequests.html')

@app.route('/logout')
def logout():
    session.pop('username')
    return  redirect(url_for('index'))

@app.route('/dashboard')
def dashboard(): #works well 
    username= session['username']
    cursor = conn.cursor()
    #q= 'SELECT timestamp, filePath, photoOwner, caption, photoID FROM follow natural join person natural join photo where username = followerUsername and photoOwner = followeeUsername '
    
    q= 'SELECT timestamp, filePath, photoOwner, caption, photoID FROM follow join person join photo where followerUsername = %s and photoOwner = followeeUsername and allFollowers =%s'
    q1 = ' union SELECT timestamp, filePath, photoOwner, caption, photoID FROM  photo where photoOwner = %s'
    q2 = ' union select timestamp, filePath, photoOwner, caption, photoID  from share natural join photo where groupName in (select groupName from belong where username = %s or groupOwner = %s) order by timestamp desc '
    
   # SELECT timestamp, filePath, photoOwner, caption, photoID  FROM belong natural join share natural join photo where username = %s order by timestamp desc '

    cursor.execute(q+q1+q2, (username, 1, username, username, username))
    data = cursor.fetchall()

    q3 = 'SELECT photoID, username, fname, lname FROM tag NATURAL JOIN photo NATURAL JOIN person WHERE acceptedTag = %s ORDER BY timestamp DESC'
    
    cursor.execute(q3, ( 1))
    tagees = cursor.fetchall()
    cursor.close()
    return  render_template('dashboard.html', username= username, posts= data, tagees = tagees)

@app.route('/seeTagRequests', methods = ['GET', 'POST'])
def seeTagRequests(): #works well
    username = session['username']
    #q = "SELECT timestamp, filePath, photoOwner, caption, photoID FROM photo natural join tag where tag.username = %s and acceptedTag=%s"
    q = "SELECT timestamp, filePath, photoOwner, caption, photo.photoID FROM photo join tag where photo.photoID = tag.photoID and tag.username = %s and acceptedTag=%s"
    cursor = conn.cursor()
    cursor.execute(q, (username, 0))
    my_requests = cursor.fetchall()
    print("\n\n\nmy_requests:\n\n", my_requests,"\n\n")
    cursor.close()
    return render_template('seeTagRequests.html', my_requests= my_requests)
           
@app.route('/acceptTag', methods = ['GET', 'POST'])
def acceptTag():#works well
    username = session['username']
    print("lets see")
    check_yes_id = request.form.get("check_yes")
    check_no_id = request.form.get("check_no")
    if check_yes_id and check_no_id:
        return render_template('seeTagRequests.html',  error= "yes and no checked together")
    elif check_yes_id:
        q = "UPDATE tag SET acceptedTag = %s WHERE photoId = %s"
        cursor = conn.cursor()
        cursor.execute(q, (1, check_yes_id))
        conn.commit()
        cursor.close()
    elif check_no_id: #check_no
        cursor = conn.cursor()
        q = "delete from tag where username =%s and photoID= %s"
        cursor.execute(q, (username, check_no_id))
        conn.commit()
        cursor.close()

    return redirect(url_for('seeTagRequests'))

@app.route('/acceptFollow', methods = ['GET', 'POST'])
def acceptFollow(): #works well
    username = session['username']
    check_yes_username = request.form.get("check_yes")
    check_no_username = request.form.get("check_no")

    if check_yes_username and check_no_username:
        return render_template('seeFollowRequests.html',  error= "accept and decline checked together")
    elif check_yes_username:
        cursor = conn.cursor()
        q = "UPDATE follow SET acceptedfollow = %s WHERE followeeUsername = %s and followerUsername = %s "
        cursor.execute(q, (1, username ,check_yes_username, ))
        conn.commit()
        cursor.close()
    elif check_no_username:
        cursor = conn.cursor()
        q = "delete from follow where followeeUsername = %s and followerUsername = %s "
        cursor.execute(q, (username, check_no_username))
        conn.commit()
        cursor.close()

    return redirect(url_for('seeFollowRequests'))

@app.route('/seeFollowRequests', methods = ['GET', 'POST'])
def seeFollowRequests():#workswell
    username = session['username']
    q = "SELECT followerUsername from follow where followeeUsername = %s and acceptedfollow = %s"
    cursor = conn.cursor()
    cursor.execute(q, (username, 0))
    my_requests = cursor.fetchall()
    cursor.close()
    return render_template('seeFollowRequests.html', my_requests= my_requests)
    
@app.route('/seeGroups', methods = ['GET', 'POST'])
def seeGroups(): #works well
    username = session['username']
    q = "SELECT groupName from closefriendgroup where groupOwner = %s"
    cursor = conn.cursor()
    cursor.execute(q, (username))
    my_requests = cursor.fetchall()
    cursor.close()
    return render_template('seeGroups.html', my_requests= my_requests)
    
@app.route('/addFriend', methods = ['GET', 'POST'])
def addFriend(): #works well
    username = session['username']
    candidate_friend = request.form.get("candidate_friend")
    if candidate_friend:
        candidate_friend =candidate_friend.strip()
    candidate_group_name  = request.form.get("group_name")
    if candidate_group_name:
        candidate_group_name = candidate_group_name.strip()

    print(candidate_friend)
    print(candidate_group_name)
    if candidate_group_name and candidate_friend: #if both of them are valid strings
        q = "SELECT groupName from closefriendgroup where groupOwner = %s" #select all groupnames the suer owns
        cursor = conn.cursor()
        cursor.execute(q, (username))
        my_requests= cursor.fetchall() #list of dictionary [{'groupName':'alig'},{'groupName':'lol}]
        my_groups_lst = [elem['groupName'] for elem in my_requests]
        print("my_groups_lst", my_groups_lst)
        q= 'SELECT username FROM person' #select all usernames
        cursor.execute(q)
        all_usernames = cursor.fetchall()
        all_usernames_lst = [elem['username'] for elem in all_usernames]
        print('all usernames lst', all_usernames_lst)
        cursor.close()
    
        if candidate_group_name not in my_groups_lst :
            error = "close friend group not found"
            return render_template('seeGroups.html', error= error, my_requests= my_requests)
        elif candidate_friend == username:
            error= "you are already in the group"
            return render_template('seeGroups.html', error= error, my_requests= my_requests)
        elif candidate_friend not in all_usernames_lst: 
            error = "username not found"
            return render_template('seeGroups.html', error= error, my_requests= my_requests)

        else: #if candidate_group_name and cadidate_friend are valid
            #check if the user is already in the group            
            cursor = conn.cursor()
            q= 'SELECT username from belong where groupName = %s and groupOwner = %s and username = %s'
            cursor.execute(q, (candidate_group_name, username, candidate_friend ))
            entry = cursor.fetchall()
            cursor.close()
            if entry: #if this username already belong to this group
                error= 'the user already exists in the group'
                return render_template('seeGroups.html', error= error, my_requests= my_requests)
            else:
                cursor = conn.cursor()
                q = 'INSERT INTO belong (groupName, groupOwner,username) VALUES (%s, %s, %s)'         
                cursor.execute(q, (candidate_group_name, username, candidate_friend ))
                conn.commit()
                cursor.close()
                return redirect(url_for('seeGroups'))
            
    else:#if one of them are none
        q = "SELECT groupName from closefriendgroup where groupOwner = %s"
        cursor = conn.cursor()
        cursor.execute(q, (username))
        my_requests= cursor.fetchall()
        error = "Please fill the all information required"
        return render_template('seeGroups.html', error= error, my_requests= my_requests)
    
@app.route('/requestToTag', methods = ['GET', 'POST'])
def requestToTag(): #works well
    username = session['username']
    candidate_username= request.form.get("candidate_username") #string
    candidate_photoID = request.form.get("candidate_photoID") #strinh
    if candidate_photoID and not candidate_username:
        error = 'please enter a username'
        return render_template('makeTagRequests.html', error= error)
    elif not candidate_photoID and candidate_username:
        error = 'please enter a photoID'
        return render_template('makeTagRequests.html', error= error)
    elif not candidate_photoID and not candidate_username:
        error = 'please enter both of the information'
        return render_template('makeTagRequests.html', error= error)
    else:
        
        if candidate_username:
            candidate_username = candidate_username.strip()
        if candidate_photoID:
            candidate_photoID = candidate_photoID.strip()
        if not candidate_photoID.isdigit(): 
            error = 'invalid photoID'
            return render_template('makeTagRequests.html', error= error)
        cursor = conn.cursor()
        q= 'SELECT username FROM person' #select all usernames
        cursor.execute(q)
        all_usernames = cursor.fetchall()
        all_usernames_lst = [elem['username'] for elem in all_usernames]
        print("all usernames lst", all_usernames_lst)

        q = 'SELECT photoID from photo'  #select all photoids
        cursor.execute(q) 
        all_photos = cursor.fetchall()
        all_photoids_lst = [str(elem['photoID']) for elem in all_photos] #integers
        #lst= [ print(type(elem)) for elem in all_photoids_lst]

        #collect visible photoIDs
        q= 'SELECT photoID FROM follow join person join photo where followerUsername = %s and photoOwner = followeeUsername and allFollowers =%s and acceptedfollow = %s'
        q1 = ' union SELECT photoID FROM  photo where photoOwner = %s'
        q2 = ' union select photoID  from share natural join photo where groupName in (select groupName from belong where username = %s or groupOwner = %s)'
        
        cursor.execute(q+q1+q2, (candidate_username, 1, 1, candidate_username, candidate_username, candidate_username))
        visible_photoIds = cursor.fetchall()
        visible_photoIds_lst = [str(elem['photoID']) for elem in visible_photoIds]
        print(visible_photoIds_lst)

        q = 'select acceptedTag from tag where username =%s and photoID =%s'
        cursor.execute(q, (candidate_username, candidate_photoID))
        data_is_in_tag_table = cursor.fetchone()
        cursor.close()

        #check if username exists
        if candidate_username not in all_usernames_lst: #check if the username exists
            error = "username not found"
            return render_template('makeTagRequests.html', error= error)
        #check if photo id exists
        elif candidate_photoID  not in all_photoids_lst:
            error = "photoID not found"
            return render_template('makeTagRequests.html', error= error)
        #check if the username can see the photo
        elif candidate_photoID  not in visible_photoIds_lst :
            error = "photo not visible to this user"
            return render_template('makeTagRequests.html', error= error)
        #check if the username is already tagged or requested to be tagged
        elif data_is_in_tag_table: #if data is already i the table
            if data_is_in_tag_table['acceptedTag'] == 1 :
                error = 'User already tagged'
                return render_template('makeTagRequests.html', error= error)
            else: # if acceptedfollow is zero
                error  ='User already has tag request for this photo'
                return render_template('makeTagRequests.html', error= error)
        #if none of tehse conditions apply, you can tag the user
        else:
            cursor = conn.cursor()
            q = 'INSERT INTO tag (username, photoID,acceptedTag) VALUES (%s, %s, %s)'         
            if candidate_username == username:
                cursor.execute(q, (candidate_username, candidate_photoID, '1' ))
            else:
                cursor.execute(q, (candidate_username, candidate_photoID, '0' ))
            conn.commit()
            cursor.close()
            return redirect(url_for('dashboard'))
        
    return redirect(url_for('dashboard'))

@app.route('/requestToFollow', methods = ['GET', 'POST'])
def requestToFollow():  #works well
    username = session['username']
    candidate_username= request.form.get("candidate_username")
    if candidate_username:
        candidate_username= candidate_username.strip()
    print(candidate_username)
    cursor = conn.cursor()
    q= 'SELECT username FROM person' #select all usernames
    cursor.execute(q)
    all_usernames = cursor.fetchall()
    all_usernames_lst = [elem['username'] for elem in all_usernames]
    cursor.close()
    print(all_usernames_lst)
    if candidate_username not in all_usernames_lst: #check if the username exists
        error = "username not found"
        print(error)
        return render_template('makeFollowRequests.html', error= error)
    else: #if it exists, check if the user is already following her or already sent the request
        q= 'SELECT acceptedfollow FROM follow where followerUsername = %s and followeeUsername = %s' #select all usernames
        cursor = conn.cursor()
        cursor.execute(q,(username, candidate_username))
        data_is_in_follow_table = cursor.fetchone()
        print(data_is_in_follow_table)
        print("closing the cursor")
        cursor.close()
        if data_is_in_follow_table: #if data is already i the table
            if data_is_in_follow_table['acceptedfollow'] == 1 :
                error = 'You are already following this user'
                return render_template('makeFollowRequests.html', error= error)
            else: # if acceptedfollow is zero
                error  ='You already requested to follow this person'
                return render_template('makeFollowRequests.html', error= error)
        else:
            if username == candidate_username: 
                error = 'You cannot follow yourself'
                return render_template('makeFollowRequests.html', error= error)
            print('data is not in the table')
            cursor = conn.cursor()
            q = 'INSERT INTO follow (followerUsername, followeeUsername,acceptedfollow) VALUES (%s, %s, %s)'         
            cursor.execute(q, (username, candidate_username, '0' ))
            conn.commit()
            cursor.close()
        
    return redirect(url_for('dashboard'))

@app.route('/postPhoto', methods=['GET', 'POST'])
def postPhoto(): #works well
    username = session["username"]
    cursor = conn.cursor()
    link = request.form.get("link")
    caption=  request.form.get("caption")
    tagee = request.form.get("tagees") #wil be None if there are nothing entered
    all_followers = request.form.get("all_followers")
    group_name_selected = request.form.get("groups_selected")
    owner_selected = request.form.get("group_owner_selected")

    if tagee:
        tagee= tagee.strip()
    if group_name_selected:
        group_name_selected = group_name_selected.strip()
    if owner_selected:
        owner_selected = owner_selected.strip()
   
    if tagee: #chck if tagee is an eixsting user
        print("\n\nif 0")
        cursor = conn.cursor()
        q= 'SELECT username FROM person' #select all usernames
        cursor.execute(q)
        all_usernames = cursor.fetchall()
        all_usernames_lst = [elem['username'].strip() for elem in all_usernames]
        print("all_usernames_lst=", all_usernames_lst)
        cursor.close()
        if tagee not in all_usernames_lst: #check if the username exists
                error = tagee + " username not found"
                print(error)
                return render_template('dashboard.html', error= error)

    #check if groups you want to post in has the user as the owner or the member
    if group_name_selected and not owner_selected:
        error = "please enter the group owner this group has"
        return render_template('dashboard.html', error= error)

    elif not group_name_selected and owner_selected:
        error= "please enter the group name this group owner has"
        return render_template('dashboard.html', error= error)
    
    elif group_name_selected and owner_selected: #check if user belongs to or owns this group
        print("\n\nif 1") 
        cursor = conn.cursor()
        print("group name selected", group_name_selected)
        q= 'select groupName, groupOwner from belong where username = %s or groupOwner = %s'
        cursor.execute(q, (username, username))
        all_groups_user_has = cursor.fetchall()
        print('all groups', all_groups_user_has)
        cursor.close()
        all_groupnames_user_has_with_owner = [(elem['groupName'] , elem['groupOwner']) for elem in all_groups_user_has]

        if (group_name_selected, owner_selected) not in all_groupnames_user_has_with_owner: #check if the username exists
            error = "you don't belong to or own a close friend group called "+ group_name_selected
            print(error)
            return render_template('dashboard.html', error= error)


    #insert the photo
    cursor = conn.cursor()  #insert photo into photo table
    q = 'INSERT INTO photo ( photoOwner, filePath, caption, allFollowers) VALUES ( %s, %s, %s, %s)'
    if all_followers=="1":
        print("all_followers ==1")
        visible_to_all_followers =True
        cursor.execute(q, (username, link, caption, all_followers ))
        print("photo posted for all followers")

        q= 'select last_insert_id();'
        cursor.execute(q)
        last_insert_id = cursor.fetchone()
        last_insert_id = last_insert_id['last_insert_id()']
        conn.commit()
    else:
        print("all_followers ==0")
        visible_to_all_followers = False
        cursor.execute(q, ( username, link, caption, '0' ))
        print("photo posted for not all followers")

        q= 'select last_insert_id();'
        cursor.execute(q)
        last_insert_id = cursor.fetchone()
        last_insert_id = last_insert_id['last_insert_id()']

        conn.commit()
    cursor.close()
    print(last_insert_id)
    
    #using the last insert id, share teh photo with the group       
    if group_name_selected and owner_selected: #share teh photo with the group
        cursor = conn.cursor()
        q = 'INSERT INTO share (groupName, groupOwner,photoID) VALUES (%s, %s, %s)'
        cursor.execute(q, ( group_name_selected, owner_selected, last_insert_id  ))
        conn.commit()
        cursor.close()

    # now that photo is posted and shared, check if tagees can be inserted
    if tagee:
        #check self tagging for your own photo
        if tagee == username:
            print('i will tag myself')
            cursor = conn.cursor()
            q = 'INSERT INTO tag (username, photoID,acceptedTag) VALUES (%s, %s, %s)'         
            cursor.execute(q, (tagee, last_insert_id , '1' ))
            print("tagging myself")
            conn.commit()
            print('tagged myself :)))')
            cursor.close()
    
            #check visibility
        else: #if you are not tagging yourself, check if user can see that photo
            cursor = conn.cursor() #check if tagee follows the user and photo is visible to all folowerss
            q= 'SELECT acceptedfollow FROM follow where followerUsername = %s and followeeUsername=%s and acceptedfollow = %s'
            cursor.execute(q, (tagee, username, 1 ))
            the_tagee_follows_the_user =  cursor.fetchall()

            if the_tagee_follows_the_user:
                the_tagee_follows_the_user = the_tagee_follows_the_user[0]['acceptedfollow']
            cursor.close()
            if the_tagee_follows_the_user and visible_to_all_followers:
                cursor = conn.cursor() #insert into tag
                q = 'INSERT INTO tag (username, photoID,acceptedTag) VALUES (%s, %s, %s)'
                cursor.execute(q, ( tagee, last_insert_id , '0' ))
                conn.commit()
                cursor.close()
    
            else: #if not , check if the  tagee belongs to any of the groups user is sharing this with
                cursor = conn.cursor()
                #get all the groups tagee has
                q= 'select groupName, groupOwner from belong where username = %s or groupOwner = %s'
                cursor.execute(q, (tagee, tagee))
                all_groups_tagee_has = cursor.fetchall()
                #print("tagee has these groups: ", all_groups_tagee_has)
                cursor.close()
                all_groups_tagee_has_with_owner = [(elem['groupName'] , elem['groupOwner']) for elem in all_groups_tagee_has]
                tagee_belongs_to_one_of_the_groups_user_has = False

                if (group_name_selected, owner_selected) in all_groups_tagee_has_with_owner:
                    tagee_belongs_to_one_of_the_groups_user_has = True

                if tagee_belongs_to_one_of_the_groups_user_has:
                    cursor = conn.cursor()
                    q = 'INSERT INTO tag (username, photoID,acceptedTag) VALUES (%s, %s, %s)'
                    cursor.execute(q, ( tagee, last_insert_id , '0' ))
                    conn.commit()
                    cursor.close()
                else:
                    #'tagee does not belong to any of the groups'
                    error = "this photo is not visible to the user you are trying to tag"
                    return render_template('dashboard.html', error= error)  ###add the requests as well!!!
                    
    return  redirect(url_for('dashboard'))

@app.route('/registerData', methods=['GET', 'POST'])
def registerData(): #workswell
    #grab data
    username= request.form['username']
    password = request.form['password']
    first_name = request.form['fname']    
    last_name = request.form['lname']    
    bio = request.form['bio']    
    avatar = request.form['avatar']    
    #is_private= request.form['is_private']
    is_private = request.form.get("is_private")

    #cursor to send queries
    cursor = conn.cursor()
    # check if username exists
    print("lest see")
    cursor.execute("SELECT * FROM person WHERE username = %s", (username))
    print("?")
    data= cursor.fetchone()
    if(data):
        error_message="Username already taken"
        cursor.close()
        return  render_template('register.html', error= error_message)
    else: 
        print("lol")
        if (is_private != None):
            cursor.execute("INSERT INTO person(username, password, fname, lname, avatar, bio, isPrivate) VALUES (%s, %s, %s, %s, %s, %s, %s)",(username, password, first_name, last_name, avatar, bio, is_private ))
            print("where is the problem2")
        else:
            cursor.execute("INSERT INTO person(username, password, fname, lname, avatar, bio) VALUES (%s, %s, %s, %s, %s, %s)",(username, password, first_name, last_name, avatar, bio ))

        conn.commit()
        print("where is the problem1")
        cursor.close()
        return render_template('home.html')

@app.route('/loginData', methods=['GET', 'POST'])
def loginData(): #workswell
    username =request.form.get("username")
    password = request.form.get("password")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM person WHERE username = %s and password = %s", (username, password))
    data = cursor.fetchone()
    cursor.close()
    if (data):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return  render_template('login.html', error= "invalid credentials")


if __name__=='__main__':
    app.secret_key='secretadmin'
    app.run(debug=True)
