# Migrating to Bento v25

## 1. Update the Bento environment 

Source the Bento virtual environment and update `bentoctl` dependencies:

```bash
source env/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 2. Set up new Bento Public files

Run the following command to generate French logo placeholder files and the new instance CSS stylesheet for 
Bento Public:

```bash
./bentoctl.bash init-web public
```

## 3. Configure new environment variables

If you have a translated logo you're adding after the above command, set `BENTO_PUBLIC_TRANSLATED_LOGO=true` in
`local.env`. Otherwise, set `BENTO_PUBLIC_TRANSLATED_LOGO=false` (optional).

If you want to adjust the height of the branding logo in Bento Public, set `BENTO_PUBLIC_LOGO_HEIGHT` to your 
desired pixel value. Otherwise, set `BENTO_PUBLIC_LOGO_HEIGHT=32` (optional).

## 4. (OPTIONAL) Add new instance styling

With the new instance CSS file in `lib/public/instance.css`, instance-specific styling can be added.

## 5. Update Bento services

Update and restart Bento services using the following commands:

```bash
./bentoctl.bash pull
./bentoctl.bash up
docker system prune -a
```
