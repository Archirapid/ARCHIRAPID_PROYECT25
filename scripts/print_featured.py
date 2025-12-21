from src import db
import json

projects = db.get_featured_projects(limit=3)
if not projects:
    print('NO_PROJECTS')
else:
    # Print the first project dict as JSON (preserve non-ascii)
    print(json.dumps(projects[0], ensure_ascii=False, indent=2))
