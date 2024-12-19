from fastapi import APIRouter, HTTPException,Depends
from ..models.project import ProjectInput,ProjectParticipant
from ..models.base_db import ProjectDB,ProjectUserLink,UserDB,AddUser,TaskInput,TasksDB,ProjectRead,TaskRead
from sqlalchemy.orm import joinedload,selectinload
from ..database import SessionDep
from sqlmodel import select
from ..utils.auth import get_current_user
router = APIRouter(tags=['projects'])

@router.post('/projects/create')
def create_project(project_data:ProjectInput, session:SessionDep,user=Depends(get_current_user)):
    #Check if the project with same name exists
    existing_project = session.exec(
        select(ProjectDB).where(ProjectDB.name == project_data.name)
    ).first()
    if existing_project:
        raise HTTPException(status_code=400, detail="A project with this name already exists")
    
    #Create a project
    project_db = ProjectDB(**project_data.model_dump(),creator_id=user.id)
    session.add(project_db) 
    project_db.participants.append(user) #Append the creator to the participants
    session.flush()
    
    #Update the user_type in the ProjectUserLink for the creator
    link_table_entry=session.exec(
        select(ProjectUserLink).where(
            ProjectUserLink.project_id==project_db.id,
            ProjectUserLink.user_id==user.id
            )
        ).first()
    if link_table_entry:
        link_table_entry.user_type="moderator"
    
    #Commit changes
    session.commit()
    session.refresh(project_db)
    return project_db
    
    
@router.get('/projects/{id}',response_model=ProjectRead)
def get_project(id:int, session:SessionDep):
    project_db= session.exec(
        select(ProjectDB).options(selectinload(ProjectDB.participants))
        .where(ProjectDB.id==id)
        ).first()
    if not project_db:
        raise HTTPException(status_code=404, detail="There is no such project")



    #FOr every user create map their type    
    user_types = {
    (link.user_id): link.user_type
    for link in session.exec(
        select(ProjectUserLink.user_id, ProjectUserLink.user_type)
        .where(ProjectUserLink.project_id == id)
    ).all()
    }
    
    participants = [
        ProjectParticipant(
            username=part.username,
            user_id=part.id,
            user_type=user_types[part.id] #Access type form precomputed dictionart
        )
        for part in project_db.participants
    ]
    print(type(project_db.tasks))
    tasks = [
    TaskRead(**task.model_dump())
        for task in project_db.tasks
    ]
    project = ProjectRead(**project_db.model_dump(), participants=participants, tasks=tasks)
    
    
    return project


@router.post('/projects/{id}/add_user')
def add_user(id:int, data:AddUser,session:SessionDep,user=Depends(get_current_user)):
    #Check if current user has a permission to add users to project
    type_check = session.exec(select(ProjectUserLink).where(ProjectUserLink.user_id==user.id, ProjectUserLink.project_id==id)).first()
    
    if not type_check or type_check=="user":
        raise HTTPException(status_code=403,detail="You do not have previlige to add users")
   
    project_db = session.get(ProjectDB,id)
    if not project_db:
        raise HTTPException(status_code=404,detail="Project not found")
    
    added_user = session.get(UserDB,data.user_id)
    if not added_user:
        raise HTTPException(status_code=404,detail="User not found")
    
    #CHeck if user exists in the project
    is_user_in_project = session.exec(
        select(ProjectUserLink)
        .where(ProjectUserLink.project_id==id,ProjectUserLink.user_id==data.user_id)
    ).first()
    if is_user_in_project:
        raise HTTPException(status_code=403, detail="THis user is already in project")
    
    #Add user to the Project
    project_db.participants.append(added_user)
    session.flush()
    #Set user type from link table entry
    link_table_entry = session.exec(select(ProjectUserLink).where(ProjectUserLink.user_id==added_user.id, ProjectUserLink.project_id==id)).first()
    if link_table_entry:
        link_table_entry.user_type=data.user_type
    else:
        raise HTTPException(status_code=500, detail="Failed to update the user's role in the project")
    session.commit()
    return {"success": True, "message": f"User {added_user.username} added to project with role {data.user_type}"}
    
    
    
@router.post('/projects/{id}/tasks/create')
def create(id:int,data:TaskInput,session:SessionDep, user=Depends(get_current_user) ):
    #Check if the user can create a task in the project
    user_project_entry = session.exec(select(ProjectUserLink).where(ProjectUserLink.user_id==user.id, ProjectUserLink.project_id==id)).first()
    if not user_project_entry:
        raise HTTPException(status_code=404, detail="Cannot add task, there is error")
    if user_project_entry.user_type=='user':
        raise HTTPException(status_code=401, detail="You do not have permission to add task")
    
    
    
    #turn input to the DB object
    user_ids = set(data.assigned_users)
    users = session.exec(select(UserDB).where(UserDB.id.in_(user_ids) )).all()
    task_db = TasksDB(title=data.title,
                      description=data.description,
                      parent_id=data.parent_id,
                      creator_id=user.id, 
                      project_id=id
                      )
    
    for user in users:
        task_db.assigned_users.append(user)
    project = session.get(ProjectDB,id)
    project.tasks.append(task_db)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    print(task_db)
    return task_db