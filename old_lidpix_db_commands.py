    if len(sys.argv) < 4 or len(sys.argv) > 5:
        show_usage()
    
    # Command newutable or newgtable: Create new table of users or galleries
    if sys.argv[1] == 'newutable' or sys.argv[1] == 'newgtable':
        if len(sys.argv) != 4:
            print "Too few or too many arguments. Needs tablename and database_file."
            show_usage()
        try:
            if sys.argv[1] == 'newutable':
                new_table(sys.argv[2], sys.argv[3], 'user_db_schema.sql')
            elif sys.argv[1] == 'newgtable':
                new_table(sys.argv[2], sys.argv[3], 'gallery_db_schema.sql')
            print "Created new table " + sys.argv[2] + " in file", sys.argv[3]
        except:
            print "Error creating table " + sys.argv[2] + " in file", sys.argv[3]
            
    # Command printtable: Show table
    if sys.argv[1] == 'printtable':
        if len(sys.argv) != 4:
            print "Too few or too many arguments."
            show_usage()
        print_table(sys.argv[2], sys.argv[3])
            
    # Command adduser: Add new user to database
    if sys.argv[1] == 'adduser':
        if len(sys.argv) != 5:
            print "Incorrect number of arguments after command 'a'"
            sys.exit(0)
        print "Adding user {u} ...".format(u=sys.argv[2])
        pw = raw_input("Please enter user's new password: ")
        pa = raw_input("Repeat password: ")
        if pw != pa:
            print "Passwords don't match"
            sys.exit(0)
        hashed_pw = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
        f = raw_input("User's full name (first and last with space between): ")
        gr = raw_input("The groups user is member of (lower case with ; between): ")
        j = time.asctime(time.localtime(time.time()))
        
        if add_user(sys.argv[2], hashed_pw, f, j, gr, sys.argv[3], sys.argv[4]):
            print "Successfully added user %s to table %s in file %s" \
            % (sys.argv[2], sys.argv[3], sys.argv[4])
        
    # Command deleteuser: Delete user
    if sys.argv[1] == 'deleteuser':
        if len(sys.argv) != 5:
            print "Incorrect number of arguments after command 'd'"
        if delete_user(sys.argv[2], sys.argv[3], sys.argv[4]):
            print "Deleted user %s from table %s in file %s" % (sys.argv[2], sys.argv[3], sys.argv[4])
