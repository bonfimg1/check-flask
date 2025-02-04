from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from flask import render_template

app = Flask(__name__)

# Configurar acesso ao Google Sheets
SHEET_ID = "1wutUPuXEnYVAOqUVOKhYlqeIWqsiSjOug-TNK5N0vSY"  # ID da sua planilha
SHEET_NAME = "check"  # Nome da aba


scope = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets",
         "https://spreadsheets.google.com/feeds"]
dic = {
    "type": "service_account",
    "project_id": "accounttocopypaste",
    "private_key_id": "283be12a520e15a0810d517f09ed59d51364ad08",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDEEV6cP5rMynLB\n48awQNSKB6v8a4Ej9D/b6bT58k8u6ya/g5s3sdsjjXSpPTR/8Gh/blrDuIEXBhy8\nz34cDiKfWtvaPULFkPITtNmeXEhkA4+miwlWCMAECn6pwXiZuHnpHEWzgo18Imix\n3PO+eV0PnnLel2qi5XS/dVpjt32nTQa83v0guCcFYWzr0whJ06YsZNnCXEErpVll\nuQyi66rPf4DEgQKwQze6eDYARpfqIJD8rPjPOTFXp1RDPTou4GJrDcPMl3qp/gJS\nRCfwCL7+wk/yYOitffRBrTFVVUbsqOXVjepI60rkHEIrTlZGYbMwu2ODhrc/L99C\n6sogeSUnAgMBAAECggEAVOJEOJcc2K6JEkIfoezfV0bNAcI1LbCv+PBsRo3OFD0A\nEIfUqj8Y5YJ3UFHMKduWEh1ftD5rvOELjf6y1UiVWrJGXmyJPOlstHVmhbXkLVCR\nX4PwLcwp/VXh0nKNWNfSB8cSsg3CXUy0UNScvgji7kEl8BJTu2RlsAIJeQRWpRfj\ntRTNzQPuWofm/3N05lRkl1i7PACJCZE/AAstpV2Ugnp56Qc3XB0B8jTF6lpywOv5\n3l4N8OnLva14EBFRcxt6ZnWEMQh/aAYYjuN05mpj9yRru1/Wu9yE6WkPo3s5nTpA\n0SAtc7TyomAdCyN1V5jMduX7hXqSfXZBW3MDBZm2gQKBgQD6TaGIrtzcsCcfM7Bb\nXSv/SiY7NI/9K2KfQJsGEwhKiANCzEvgdWqlTDSGjmV6p9SsNv+eyUlyxxrRj0iT\ncyugM2kpiY+7jMNzEAdfWbRjdIs198Zi7bN5kU40NAYGdIwBaEIE4Wx245qSxJNE\n+IfwgP9gcvUCFrldapilwCuIwQKBgQDIh72x7UMQ0XxMsk/NveWVi2hYC1BygL2l\nkhm04k7kKbg9QJFzOSxo+DuCe9ia3n/Ni3RhOTuS75CLyK+yCOeWd49t9vHoYQ58\n1/foDOcZRc1LOflAGyAEIb21UFiP9rqk5RvDlqBO40HkIvBegGKiPBPxa9dxr7AX\napV7pZl/5wKBgGnMKGvypW4uksqweWmUz0T/3XsG85mqHex8TUpa/xUpul8gpS3B\n04r80/LP+3rFt7H3KUK/h+kY2XAcZSvV8WmscVXaTEOU8wQOkV8vNn0XRMRR76vf\nFw5aabjNCILv/kGWBNm1QrhZ6fsBVdJATo1MqSTmUkNIwZ8HsG/W80/BAoGAWi55\nh+f8zjZ3oQJb01oAQsWkElxcPHJbV3eh6fAQrJl6islb4CapKzffg2nw2o0Pir+Z\nghO8D/N+3O5O3VEV3Vw9e6Wf2vKzEkAJ9CjBUWNL1PXoewT33APUjhLpES1TeM60\nMrytsWyQeGmiEc3JDc7Y5SyrgiwRlCZRvX6WzqcCgYAYf7dTtcOJ8GaV5HUHEuyl\n9zjJKzbwKbudurOHQrlbNRWMIg+oTFmWQfVlL0XV1fU0ZWGBYFFnRZnscUNroxH1\ntaW725Mdb9+1NMc5L7HSwEjE/p16Lyts+aP3bY6xChA5BXoQcrKInnUPQgYHVq54\nzO1kX7QTqxpYhQcYcyzuaQ==\n-----END PRIVATE KEY-----\n",
    "client_email": "accountcopypastebot@accounttocopypaste.iam.gserviceaccount.com",
    "client_id": "115883670061446057641",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/accountcopypastebot%40accounttocopypaste.iam.gserviceaccount.com",
}
creds = ServiceAccountCredentials.from_json_keyfile_dict(dic, scope)
client = gspread.authorize(creds)

# Função para determinar o turno com base na hora atual
def get_turno():
    agora = datetime.utcnow() - timedelta(hours=3)  # Ajusta para horário de Brasília
    hora = agora.hour
    minuto = agora.minute

    if 5 <= hora < 12 or (hora == 12 and minuto == 0):
        return "1º Turno"
    elif 12 <= hora < 18 or (hora == 18 and minuto <= 15):
        return "2º Turno"
    elif 18 <= hora < 22 or (hora == 22 and minuto <= 11):
        return "3º Turno"
    else:
        return "4º Turno"




@app.route("/checklist", methods=["GET"])
def check_list():
    try:
        maquina = request.args.get("maquina")  # Parâmetro da máquina na URL
        if not maquina:
            return jsonify({"error": "Parâmetro 'maquina' é obrigatório"}), 400

        # Obtém os dados do Google Sheets
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_values()

        hoje = datetime.utcnow().strftime("%Y-%m-%d")  # Data de hoje no formato correto
        turno = get_turno()  # Obtém o turno atual

        # Percorre a planilha e verifica se há check-list registrado para a máquina
        for linha in data[1:]:  # Ignorar cabeçalho
            data_linha = datetime.strptime(linha[0], "%d/%m/%y").strftime("%Y-%m-%d")
            if data_linha == hoje and linha[1] == turno and maquina in linha[2]:
                return render_template("status.html",
                                       status_class="positive",
                                       status_message="Check-list realizado com sucesso!",
                                       detailed_message="A máquina foi verificada no turno atual.")

        return render_template("status.html",
                               status_class="negative",
                               status_message="Check-list não encontrado",
                               detailed_message="Não há registros de check-list para a máquina no turno atual.")

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
