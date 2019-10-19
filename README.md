# ImageTrick
Тема задачі-проекту: Планування та обробка даних польотів дронів

Офіційний сайт:
https://www.facebook.com/TUI.Info/ <br>
Завдання:
https://docs.google.com/document/d/1RylgSLtmbqYr-IrfhLpDRTKZaclhvRWSXMek-qaKy7k/edit?fbclid=IwAR1Bxok4yXfWWgASUke0ajelEA0OysSdYdJ2Z1SXJGCbpuzWKMZnU7CaOHk#bookmark=id.gjdgxs<br>
Тестові зображення:
https://drive.google.com/drive/folders/1O4PgiB72-AdqDoYVmNHvkOy_1Am_igBO

## Передумови
* ``` Python ```

## Установка
  ### Linux (Протестовано на Linux Mint 19.2):
  * ``` cd Path/ImageTrick/main ```
  * ``` conda create -n new_environment python=3.6 ```
  * ``` conda activate new_environment ```
  * ``` while read requirement; do conda install --yes $requirement || pip install $requirement; done < requirements.txt ```
  * ``` ./TUIprogram.sh ```
  
## Допомога користувачу
   ### Завдання 1:
   
   ### Завдання 2:
   * Оберіть зображення за допомогою команди: Файл > Відкрити файл(и) > Потрібна папка > Вибрати файли > Відкрити.
   * Натиснути Файл > Дія > Фокус-стекінг.
   * Отриманий результат зберігається у папці ```Path/ImageTrick/main/OutputFocus ```.
   
   ### Завдання 4:
   * Оберіть зображення за допомогою команди: Файл > Відкрити файл(и) > Потрібна папка > Вибрати файли > Відкрити.
   * Натиснути Файл > Дія > Зробити відео.
   * Вибрати, скільки FPS, або кадрів у секунду буде містити відео.
   * Отриманий результат зберігається у папці ```Path/ImageTrick/main/OutputVideo ```.
   
   ### Завдання 5:
   * Оберіть зображення за допомогою команди: Файл > Відкрити файл(и) > Потрібна папка > Вибрати файли > Відкрити.
   * Натиснути Файл > Дія > Оптичний потік.
   * Вибрати, скільки FPS, або кадрів у секунду буде містити відео.
   * Отриманий результат зберігається у папці ```Path/ImageTrick/main/OutputFLow ```.
   
   ### Завдання 6:
   * Оберіть зображення за допомогою команди: Файл > Відкрити файл(и) > Потрібна папка > Вибрати файл > Відкрити.
   * Натиснути кнопку ``` знайти кольори ```.
   * Натиснути на певний колір.
   * Появиться зображення у вікні, де вибраний колір зафарбований чорним.
   * За допомогою даних про яскравість кольору та маски визначити, яку ділянку поля потрібно полити.
  
   
