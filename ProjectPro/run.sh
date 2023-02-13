if ! grep -q FLASK_RUN_PORT ".env" || ! [[ -d .venv ]]; then
    echo Run setup.sh first
    exit 1
fi


app=$1

if [[ -z $app ]]; then
    app=app
fi

# activate the virtual environment for the coursework
source .venv/bin/activate

# run Flask for the coursework
echo Running Flask
FLASK_APP=$app flask run
