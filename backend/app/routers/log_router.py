from datetime import datetime
from fastapi import APIRouter, Query
from app.database import Database
from app.utils.response import success, error, paginated

router = APIRouter(tags=["日志查询"])


@router.get("/raw")
def query_raw_records(
    vendor_code: str = Query(None),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        collection = Database.get_collection("raw_records")
        query = {}
        if vendor_code:
            query["vendorCode"] = vendor_code
        if status:
            query["status"] = status

        total = collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = collection.find(query).sort("createdAt", -1).skip(skip).limit(page_size)
        items = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            items.append(doc)

        return paginated(items, total, page, page_size)
    except Exception as e:
        return error(str(e), code=500)


@router.get("/temperature")
def query_temperature_records(
    vendor_code: str = Query(None),
    patient_id: str = Query(None),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        collection = Database.get_collection("temperature_records")
        query = {}
        if vendor_code:
            query["vendorCode"] = vendor_code
        if patient_id:
            query["patientId"] = patient_id
        if status:
            query["status"] = status

        total = collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = collection.find(query).sort("createdAt", -1).skip(skip).limit(page_size)
        items = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            items.append(doc)

        return paginated(items, total, page, page_size)
    except Exception as e:
        return error(str(e), code=500)


@router.get("/transform")
def query_transform_logs(
    vendor_code: str = Query(None),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        collection = Database.get_collection("transform_logs")
        query = {}
        if vendor_code:
            query["vendorCode"] = vendor_code
        if status:
            query["status"] = status

        total = collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = collection.find(query).sort("createdAt", -1).skip(skip).limit(page_size)
        items = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            items.append(doc)

        return paginated(items, total, page, page_size)
    except Exception as e:
        return error(str(e), code=500)


@router.get("/unmatched")
def query_unmatched_items(
    vendor_code: str = Query(None),
    status: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        collection = Database.get_collection("unmatched_items")
        query = {}
        if vendor_code:
            query["vendorCode"] = vendor_code
        if status:
            query["status"] = status

        total = collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = collection.find(query).sort("createdAt", -1).skip(skip).limit(page_size)
        items = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            items.append(doc)

        return paginated(items, total, page, page_size)
    except Exception as e:
        return error(str(e), code=500)


@router.get("/retry-tasks")
def query_retry_tasks(
    status: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    try:
        collection = Database.get_collection("retry_tasks")
        query = {}
        if status:
            query["status"] = status

        total = collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = collection.find(query).sort("createdAt", -1).skip(skip).limit(page_size)
        items = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            items.append(doc)

        return paginated(items, total, page, page_size)
    except Exception as e:
        return error(str(e), code=500)
