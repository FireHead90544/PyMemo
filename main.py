from dataclasses import Memo, Database, Utils
import datetime, outputformat as ouf, json, math

db = Database()
db.initialize_db() # Initializes the db, creates the memo table

utils = Utils() # Our favourite utilities this application utilizes for its proper functioning.

def main():
    """
    The Parent Function. The Supreme Director of everything.
    """
    utils.clear_console()
    options = ["1. Add a memo.", "2. Update a memo.",
                "3. Delete a memo.", "4. View a memo.",
                "5. View all memos.", "6. Reset the database.",
                "7. Exit."]
    ouf.bigtitle("PyMemo")
    ouf.boxtitle("Developer: </Rudransh Joshi>")
    ouf.showlist(options, style="box", title="Select an option")

    select_option()

def select_option():
    """
    Choices mapped to their respective functions.
    Basically some big brain stuff, which pathetic brain can't understand.
    """
    optionMaps = {
        1: add_memo,
        2: update_memo,
        3: delete_memo,
        4: view_memo,
        5: view_all_memos,
        6: reset_db,
        7: exit
    }
    option = int(input(">>> Select an option [1-7]:\t"))
    optionMaps[option]()

def add_memo():
    """
    Adds memo to the database assigning a unique id to it.
    Also, saves the memo as an image ("memos/memo_<id>.png")
    """
    utils.clear_console()
    ouf.boxtitle("Add a Memo")
    print("\n")
    name = input(">>> Enter the name of the memo (Max. 30 Characters):\t")[:30]
    text = input(">>> Enter the text of the memo (Max. 420 Characters):\t")[:420]
    items = [i.strip() for i in input(">>> Enter the items of the memo (Upto 5, separated by a comma):\t\t").split(",")[0:5]]
    author = input(">>> Enter the author of the memo (Max. 32 Characters):\t")[:32]

    db.cur.execute("INSERT INTO memos (name, memotext, items, author) VALUES (?, ?, ?, ?)", (name, text, json.dumps(items), author))
    db.conn.commit()
    memo_id = db.cur.lastrowid
    db.cur.execute("SELECT * FROM memos WHERE id = ?", (memo_id,))
    memo = db.cur.fetchone()
    memo = Memo(memo[0], memo[1], memo[2], json.loads(memo[3]), memo[4], utils.parse_timestamp(memo[5]))
    memo.save_memo_as_image()
    ouf.linetitle(f"\nCreated memo with memo id '{memo_id}', saved it to 'memos/memo_{memo_id}.png' as well", style="double")
    utils.sleep(3)
    main()

def update_memo():
    """
    Updates a memo, updates the saved image of the memo as well.
    """
    utils.clear_console()
    ouf.boxtitle("Update a Memo")
    print("\n")
    memo_id = input(">>> Enter the memo id:\t")
    db.cur.execute("SELECT * FROM memos WHERE id = ?", (memo_id))
    memo = db.cur.fetchone()

    if not memo:
        ouf.linetitle(f"\nNo memo found with id: {memo_id}", style="double")
        utils.sleep(2)
        main()
    else:
        print("\n")
        name = input(">>> Enter the name of the memo (Max. 30 Characters):\t")[:30]
        text = input(">>> Enter the text of the memo (Max. 420 Characters):\t")[:420]
        items = [i.strip() for i in input(">>> Enter the items of the memo (Upto 5, separated by a comma):\t\t").split(",")[0:5]]
        author = input(">>> Enter the author of the memo (Max. 32 Characters):\t")[:32]

        db.cur.execute("UPDATE memos SET name = ?, memotext = ?, items = ?, author = ? WHERE id = ?", (name, text, json.dumps(items), author, memo_id))
        db.conn.commit()

        db.cur.execute("SELECT * FROM memos WHERE id = ?", (memo_id,))
        memo = db.cur.fetchone()
        memo = Memo(memo[0], memo[1], memo[2], json.loads(memo[3]), memo[4], utils.parse_timestamp(memo[5]))
        memo.save_memo_as_image()

        ouf.linetitle(f"\nUpdated memo with memo id '{memo_id}', updated 'memos/memo_{memo_id}.png' as well.", style="double")
        utils.sleep(3)
        main()

def delete_memo():
    """
    It is what it is.
    Deletes a memo from the database.
    """
    utils.clear_console()
    ouf.boxtitle("Delete a Memo")
    print("\n")
    memo_id = input(">>> Enter the memo id:\t")
    db.cur.execute("SELECT * FROM memos WHERE id = ?", (memo_id))
    memo = db.cur.fetchone()
    if not memo:
        ouf.linetitle(f"\nNo memo found with id: {memo_id}", style="double")
        utils.sleep(2)
        main()
    else:
        db.cur.execute("DELETE FROM memos WHERE id = ?", (memo_id))
        db.conn.commit()
        ouf.linetitle(f"\nDeleted memo with id '{memo_id}'", style="double")
        utils.sleep(3)
        main()

def view_memo():
    """
    Probably the best function.
    Shows a memo, either in the console or as an image.
    """
    utils.clear_console()
    ouf.boxtitle("View a Memo")
    print("\n")
    memo_id = input(">>> Enter the memo id:\t")
    db.cur.execute("SELECT * FROM memos WHERE id = ?", (memo_id))
    memo = db.cur.fetchone()
    if not memo:
        ouf.linetitle(f"\nNo memo found with id: {memo_id}", style="double")
        utils.sleep(2)
        main()
    else:
        memo = Memo(memo[0], memo[1], memo[2], json.loads(memo[3]), memo[4], utils.parse_timestamp(memo[5]))
        view_type = input(">>> Enter '1' to view memo in terminal, or '2' to view it as an image:\t")
        if view_type == "1":
            utils.clear_console()
            print(memo.get_memo())
        elif view_type == "2":
            memo.show_memo_as_image()
        input("\n>>> Press 'Enter' to go back to main menu.")
        main()
        


def view_all_memos():
    """
    Most complex function, pretty intellectual one to be honest.
    Paginates and shows all the memos available in the database.
    """
    utils.clear_console()
    ouf.boxtitle("View all Memos")
    print("\n")
    db.cur.execute("SELECT * FROM memos")
    memos = db.cur.fetchall()
    if not memos:
        ouf.linetitle("\nNo memos found.", style="double")
        utils.sleep(2)
        main()
    else:
        page = 0
        while True:
            utils.clear_console()
            ouf.boxtitle(f"View all Memos - Page {page+1}")
            print("\n")
            for i in range(20*page, 20*(page+1)):
                if i < len(memos):
                    print(f"Memo ID: {memos[i][0]}\tMemo Name: {memos[i][1]}")
            print("\n")
            if page == 0:
                print("0 - Go back to main menu")
            else:
                print("0 - Go back to previous page")
            if page == math.ceil(len(memos)/20)-1:
                print("1 - Go to next page")
            else:
                print("1 - Go to next page")
            print("\n")
            choice = input(">>> Enter your choice:\t")
            if choice == "0":
                main()
            elif choice == "1":
                page += 1
            else:
                ouf.linetitle("\nInvalid choice, returning to main menu.", style="double")
                utils.sleep(2)
                main()

def reset_db():
    """
    Most dangerous function (definitely not exeggerating).
    Resets the database deleting everything and starting everything from scratch.
    """
    utils.clear_console()
    ouf.boxtitle("Reset the Database | Proceed with Caution")
    print("\n")
    ouf.boxtitle("This will delete all memos and reset the database.", style="double")
    print("\n")
    final = input(">>> Enter 1 to 'continue' or anything else to 'abort this operation':\t")

    db.reset_db() if final == "1" else main()
    main()

main()
