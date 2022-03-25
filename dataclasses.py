from pathlib import Path
import outputformat as ouf
from PIL import Image, ImageDraw, ImageFont
import io, os, sys, textwrap, datetime, sqlite3, time

class Utils:
    def __init__(self):
        pass

    def clear_console(self) -> None:
        """
        Clears the console.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def sleep(self, seconds) -> None:
        """
        Sleeps for a specified number of seconds.
        """
        time.sleep(seconds)

    def parse_timestamp(self, s) -> datetime.datetime:
        """
        Parses the string timestamp returned by db to a datetime object,
        """
        pattern = "%Y-%m-%d %H:%M:%S"
        return datetime.datetime.strptime(s, pattern)

class Database:
    """
    Represents a SQLite3 Database object.
    Contains methods and functions related to the database management.
    """
    def __init__(self) -> None:
        self.dbpath = Path(__file__).parent / "memo.db"

    def initialize_db(self) -> None:
        """
        Initializes the database, creates the connection, cursor and tables.
        """
        self.conn = sqlite3.connect(self.dbpath, detect_types=sqlite3.PARSE_DECLTYPES)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_table(self, tablename: str, columns: str) -> None:
        """
        Create table with specified columns in a specified table.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS {}{}
        """.format(tablename, columns))
        self.conn.commit()

    def create_tables(self) -> None:
        """
        Create the memos tables.
        """
        self.create_table("memos", "(id INTEGER PRIMARY KEY, name VARCHAR(30), memotext VARCHAR(420), items VARCHAR(200), author VARCHAR(32), timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")

    def drop_table(self, table: str) -> None:
        """
        Drop a specified table.
        """
        self.cur.execute("DROP TABLE IF EXISTS {}".format(table))
        self.conn.commit()

    def reset_db(self) -> None:
        """
        Resets the database.
        Deletes all tables and records.
        Deletes the database.
        Reinitializes the database.
        """
        self.drop_table("memos")
        self.conn.close()
        os.remove(self.dbpath)
        self.initialize_db()


class Memo:
    def __init__(self, mid: str, name: str, text: str, items: list, author: str, timestamp: datetime.datetime) -> None:
        self.id = str(mid)
        self.name = name
        self.text = "\n".join(textwrap.wrap(text, width=40))
        self.items = items
        self.author = author
        self.timestamp = timestamp.strftime("%d-%B-%Y, %I:%M %p")


    def get_memo(self) -> str:
        """
        Get the memo as a string.
        Writes the memo in the buffer because of some unicode characters,
        later reads it and sets the buffer to previous state.
        """
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        ouf.bigtitle('PyMEMO')
        ouf.boxtitle(self.id + ' | ' + self.name)
        print(f"\n{self.text}\n")
        ouf.showlist(self.items, "box", "Items")
        print(self.author)
        ouf.linetitle(self.timestamp, style="double")

        sys.stdout = old_stdout

        return u"{}".format(buffer.getvalue()[0:-1])
    

    def get_memo_as_image(self) -> Image:
        """
        Get the memo as an image.
        Draws the text in an image of dimensions (490x800px).
        """
        img = Image.new('RGB', (490, 800), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((50, 70),
                    self.get_memo(),
                    fill=(0, 0, 0),
                    font=ImageFont.truetype(str(Path("fonts/unifont.ttf").resolve()),
                    size=20))
        return img


    def show_memo_as_image(self) -> None:
        """
        Displays the memo as an image.
        """
        self.get_memo_as_image().show()
    

    def save_memo_as_image(self) -> None:
        """
        Saves the memo as an image inside the memos folder with name memo_{id}.png.
        """
        Path("memos").mkdir(parents=True, exist_ok=True)
        self.get_memo_as_image().save(f"memos/memo_{self.id}.png", format='PNG')
