import json
import base64
import xmltodict
from Bio.Blast.Applications import NcbiblastnCommandline


class BlastService:
    def __init__(self):
        pass

    def run_local_blast(self, query_file, db_path, output_file, outfmt):
        blastn_cline = NcbiblastnCommandline(query=query_file, db=db_path, evalue=0.001, outfmt=outfmt, out=output_file)
        stdout, stderr = blastn_cline()
        print(stdout, stderr)

    def process_request(self, message):
        message_body = json.loads(message)
        user_id = message_body['user_id']
        outfmt = message_body['outfmt']
        file_base64 = message_body['file']
        print(f"user_id: {user_id} request recieved from gateway..")
        file_data = base64.b64decode(file_base64.encode())
        query_file = "input.fa"
        output_file = "blast_output.tabular"
        db_path = "./blastTestDB/testDB_addUIC"

        with open(query_file, 'wb') as f:
            f.write(file_data)

        self.run_local_blast(query_file, db_path, output_file, outfmt)

        with open(output_file, 'r') as f:
            xml_string = f.read()

        blast_result = json.dumps(xmltodict.parse(xml_string), indent=4)
        response = {
            "user_id": user_id,
            "blast_result": blast_result
        }


        return response
