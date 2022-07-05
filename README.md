# Setup pre-commit
First install `pre-commit` by running:
```sh
pip install pre-commit
```

Then to install the git hook run:
```sh
pre-commit install -t pre-commit -t commit-msg
```

Now `pre-commit` will run on every `git commit`.
# demo
[youtube link](https://youtu.be/8zv-x2LzxBk)
# run
- add some images in `resources/images`
- `docker-compose up --build`
- open `http://127.0.0.1:8080/` on your browser


# dev
To allow the development of the project, you can build wihout `docker-compose`:
to do so, you'll need another resource folder

- add a .env in `backend/.env` which contains the following variables:
  - `DIRECTORY_PATH=resources/`
- copy your usual `resources/` in `backend/resources/`


- `cd frontend && npm install && npm run dev`
- `cd backend && pip install -r requirements.txt && uvicorn src.app:app --reload --host 127.0.0.1 --port 1337`
