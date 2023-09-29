#!/bin/bash -ex

# Função para verificar e instalar uma dependência se não estiver presente
check_install_dependency() {
    local command_name="$1"
    local package_name="$2"

    if ! command -v "$command_name" &> /dev/null; then
        echo "O comando $command_name não está instalado. Instalando $package_name..."
        sudo apt-get install "$package_name" -y  # Use o gerenciador de pacotes apropriado para sua distribuição
    fi
}

# Verificar e instalar as dependências necessárias
check_install_dependency "wget" "wget"
check_install_dependency "unzip" "unzip"
check_install_dependency "curl" "curl"

# Especificar a versão do Google Chrome desejada
CHROME_VERSION="117.0.5938.62-1"  # Substitua pela versão desejada

# Baixar e instalar o Google Chrome Stable na versão especificada
#http://170.210.201.179/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_117.0.5938.62-1_amd64.deb
wget "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb"
sudo dpkg -i "google-chrome-stable_${CHROME_VERSION}_amd64.deb"
sudo apt-get install -f -y

# Baixar e instalar o Chromedriver compatível com a versão do Chrome
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.92/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip
chmod +x chromedriver-linux64/chromedriver


# Limpar arquivos de instalação desnecessários
rm -rf "google-chrome-stable_${CHROME_VERSION}_amd64.deb" chromedriver-linux64.zip
