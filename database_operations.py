import pyodbc

class DatabaseOperations:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def get_documents_for_file_number(self, file_number):
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()

        # Use placeholders for file_number
        query = """
            SELECT D.DocumentPath, D.DocumentName, I.FILENO, I.CMT, I.LLCode_Field ,I.DDATE_Field
            FROM IndexForm_CLS I JOIN Document D ON I.DocumentID = D.DocumentID
            WHERE I.FILENO = ? AND I.CMT = 'Tax Garnishment'
            AND (I.LLCode_Field='XITG' or I.LLCode_Field='XITG2' or I.LLCode_Field = ' XITG')
            AND CONVERT(DATE, I.DDATE_Field, 101) BETWEEN '06/19/2023' AND '03/01/2024'
        """

        # Include only file_number in execute
        documents = cursor.execute(query, file_number).fetchall()

        conn.close()
        return documents
