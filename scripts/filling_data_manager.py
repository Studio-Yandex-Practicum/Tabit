import argparse


def main():
    parser = argparse.ArgumentParser(description='Заполнение базы данных')
    parser.add_argument(
        '-c',
        '--companies',
    )
    parser.add_argument('-cu', '--company-users')
    parser.add_argument('-tu', '--tabit-users')
