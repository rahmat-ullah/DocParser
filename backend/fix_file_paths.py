import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update, select
from app.models.document import Document
from app.core.config import get_settings

async def fix_file_paths():
    settings = get_settings()
    # For SQLite, we need to use the aiosqlite driver
    database_url = settings.database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    engine = create_async_engine(database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get all documents with empty file_path
        result = await session.execute(
            select(Document).where(
                (Document.file_path == None) | (Document.file_path == "")
            )
        )
        documents = result.scalars().all()
        
        fixed_count = 0
        for doc in documents:
            # Check if file exists in uploads directory
            expected_path = os.path.join(settings.upload_dir, doc.filename)
            if os.path.exists(expected_path):
                doc.file_path = os.path.abspath(expected_path)
                fixed_count += 1
                print(f"Fixed document {doc.id}: {doc.file_path}")
        
        await session.commit()
        print(f"\nFixed {fixed_count} documents")
        
        # Also fix the specific document
        specific_file = os.path.abspath(os.path.join(settings.upload_dir, "a339a0f1-fd45-4278-98e0-aff8b743f409.pdf"))
        if os.path.exists(specific_file):
            result = await session.execute(
                update(Document)
                .where(Document.id == "a339a0f1-fd45-4278-98e0-aff8b743f409")
                .values(file_path=specific_file)
            )
            await session.commit()
            print(f"\nSpecifically updated document a339a0f1-fd45-4278-98e0-aff8b743f409")

if __name__ == "__main__":
    asyncio.run(fix_file_paths())
