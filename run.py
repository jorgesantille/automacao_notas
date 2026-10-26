from extrair_nota import app

if __name__ == '__main__':
    print("A iniciar o servidor de recibos em segundo plano...")
    app.run(host='0.0.0.0', port=5000)