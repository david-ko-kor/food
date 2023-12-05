
from flask import Flask, render_template,g,request
import sqlite3
def connet_db():
    sql = sqlite3.connect('food_log.db')
    sql.row_factory=sqlite3.Row
    return sql
def get_db():
    if not hasattr(g,'sqlite3_db'):
            g.sqlite_db = connet_db()
    return g.sqlite_db
