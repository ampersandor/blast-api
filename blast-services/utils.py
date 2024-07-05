import json
import base64
import xmltodict
import subprocess
import os


class BlastService:
    def __init__(self, db_path="./blastTestDB/testDB_addUIC"):
        self.db_path = db_path

    def run_local_blast(self, query_file, output_file, outfmt, evalue=0.001):
        blast_command = [
            "blastn",
            "-query",
            query_file,
            "-db",
            self.db_path,
            "-evalue",
            str(evalue),
            "-outfmt",
            str(outfmt),
            "-out",
            output_file,
        ]

        try:
            result = subprocess.run(
                blast_command, check=True, capture_output=True, text=True
            )
            print(f"BLAST stdout: {result}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"BLAST error occurred: {e}")
            print(f"BLAST stderr output:\n{e.stderr}")
            return False

    def decode_and_save_file(self, file_base64, filename):
        file_data = base64.b64decode(file_base64.encode())
        with open(filename, "wb") as f:
            f.write(file_data)

    def read_file(self, filename):
        with open(filename, "r") as f:
            return f.read()

    def process_request(self, message):
        message_body = json.loads(message)
        user_id = message_body["user_id"]
        outfmt = message_body["outfmt"]
        file_base64 = message_body["file"]

        print(f"user_id: {user_id} request received from gateway..")

        buffer_file = "input.fa"
        output_file = "blast_output.tabular"

        self.decode_and_save_file(file_base64, buffer_file)

        if not self.run_local_blast(buffer_file, output_file, outfmt):
            return {"error": "BLAST execution failed"}

        blast_result = self.read_file(output_file)

        try:
            parsed_result = json.dumps(xmltodict.parse(blast_result), indent=4)
        except Exception as e:
            print(f"Error parsing BLAST result: {e}")
            parsed_result = blast_result  # Return raw result if parsing fails

        response = {"user_id": user_id, "blast_result": parsed_result}

        # Clean up temporary files
        os.remove(buffer_file)
        os.remove(output_file)

        return response


# Usage
# blast_service = BlastService()
# response = blast_service.process_request(message)
if __name__ == "__main__":
    bs = BlastService()
    bs.run_local_blast("../test.fa", "output.tabular", 7)
