
SECRET_KEY="eval shuf -zern 50 {A..Z} {0..9} {a..z}"
setting_file="recruitr/local_settings.py"


create_secret_key() {
    touch $setting_file
    echo "SECRET_KEY = ''" > $setting_file

    sed -i "s/^SECRET_KEY \?= \?.*/SECRET_KEY = '$($SECRET_KEY)'/" $setting_file
}


edit_secret_key() {
    if grep SECRET_KEY $setting_file 1> /dev/null 2>&1; then
        sed -i "s/^SECRET_KEY \?= \?.*/SECRET_KEY = '$($SECRET_KEY)'/" $setting_file     
    else
        echo "SECRET_KEY = ''" >> $setting_file
        sed -i "s/^SECRET_KEY \?= \?.*/SECRET_KEY = '$($SECRET_KEY)'/" $setting_file 
    fi
}


if ls $setting_file 1> /dev/null 2>&1; then
    edit_secret_key
else
    create_secret_key
fi