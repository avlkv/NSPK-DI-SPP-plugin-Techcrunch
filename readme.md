# <Название плагина>

## Для создателей плагинов

`Этот раздел можно вырезать из своего репозитория`

### Основные правила
1. В этой инструкции могут встречаться параметры в `< >`. Всё, что находится внутри скобок должно быть единым текстом, все проблемы и тире должны быть заменены на `_`.
Например `<ref name>` означает, что тут должно быть уникальное имя связанного объекта.
2. Нагрузка должна быть протестирована перед передачей в платформу.
3. Нагрузка должна перехватывать только те ошибки и exception, которые она непосредственно обрабатывает. Всё остальное должно пропускаться во вне нагрузки, их поймает и обработает платформа
   1. Все перехватываемые ошибки должны быть ожидаемыми. Например, если нам нужен `title`, а парсинг этой области вызывает ошибку, тогда нужно либо пропустить эту страницу/документ или выкинуть ошибку парсинга. 


### Deploy
1. Необходимо слить изменения мз `dev` ветки (на которой ведется разработка) в `main` ветку.
2. Из `main` ветки нужно удалить все лишние файлы.
3. Из `main` ветки сделать релиз, с кратким описанием изменений и обновленным тегом.
4. Передать ссылку на репозиторий админу платформы.


### Типы плагинов
Можно использовать 2 типа плагинов:
1. PARSER - плагин с парсером, обрабатывающим документы источника
2. ML - плагин с моделью, которая обрабатывает установленные источники (их документы)

### Инструкции

Список всех инструкций и их описание можно увидеть [тут](all_commands.md).


### Дерево репозитория
Файлы помеченный `(*)` являются обязательными для платформы. Остальные не обрабатываются. Они служат для удобства написания и тестирования плагина.
```bash
└── NSPK-DI-SPP-plugin-<ref name>
    ├── src
    │   └── spp
    │       └── types.py # Содержит датакласс SPP_document. Объект, который необходимо использовать при заполнении списка документов источника
    ├── .gitignore # Содержит информацию о том, что не должен обрабатывать git (например, метаданные IDE и виртуальные окружения python)  
    ├── LICENSE # Лицензия MIT  
    ├── readme.parser.md # Инструкция по созданию плагинов типа PARSER
    ├── all_commands.md # Список всех доступных инструкций и их описание
    ├── <ref name>.py # Класс нагрузки плагина.    
    └── SPPfile.general # Общая структура конфигурации для платформы
    └── SPPfile.default # (*) Файл конфигурации для платформы. Конфигурация по умолчанию
```