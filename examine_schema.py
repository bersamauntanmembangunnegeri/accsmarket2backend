import psycopg2
import sys

# Database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_xmqt6HUj4Sda@ep-curly-mode-adt3b4gn-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def examine_schema():
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("=== DATABASE SCHEMA EXAMINATION ===\n")
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("TABLES IN DATABASE:")
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # Examine each table structure
        for table in tables:
            table_name = table[0]
            print(f"=== TABLE: {table_name.upper()} ===")
            
            # Get column information
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable, 
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            print("COLUMNS:")
            for col in columns:
                col_name, data_type, nullable, default, max_length = col
                length_info = f"({max_length})" if max_length else ""
                nullable_info = "NULL" if nullable == "YES" else "NOT NULL"
                default_info = f" DEFAULT {default}" if default else ""
                print(f"  {col_name}: {data_type}{length_info} {nullable_info}{default_info}")
            
            # Get foreign keys
            cursor.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = %s;
            """, (table_name,))
            
            foreign_keys = cursor.fetchall()
            if foreign_keys:
                print("FOREIGN KEYS:")
                for fk in foreign_keys:
                    col_name, ref_table, ref_col = fk
                    print(f"  {col_name} -> {ref_table}.{ref_col}")
            
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error examining schema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    examine_schema()

