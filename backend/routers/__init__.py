# routers/__init__.py
from .companies import router as companies_router
from .documents import router as documents_router
from .financial import router as financial_router
from .invoices import router as invoices_router
from .anomalies import router as anomalies_router
from .chat import router as chat_router
from .tax import router as tax_router
from .bank_statements import router as bank_statements_router

all_routers = [
    companies_router,
    documents_router,
    financial_router,
    invoices_router,
    anomalies_router,
    chat_router,
    tax_router,
    bank_statements_router,
]