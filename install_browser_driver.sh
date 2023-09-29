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

# Instalar o Google Chrome Stable
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Baixar e instalar o Chromedriver compatível com a versão do Chrome
CHROME_VERSION=$(google-chrome-stable --version | awk '{print $3}')
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
chmod +x chromedriver

# Mover o Chromedriver para uma pasta específica do projeto
DEST_DIR="/driver"
mv chromedriver "$DEST_DIR"

# Limpar arquivos de instalação desnecessários
rm -rf google-chrome-stable_current_amd64.deb chromedriver_linux64.zip
