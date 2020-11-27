# Bot przypominajka
[![](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/release/python-378/) [![](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

Ring to bot umożliwiający przypomnienie nauczycielowi o końcu lekcji. Został wyposażony w funkcję tłumacza google w kilku niezbędnych językach (angielski, rosyjski, hiszpański i niemiecki). Bot potrzebuje uprawnień administratora. Został napisany w języku Python (domyślnie 3.7) na Windowsie, ale na Linuksie powinien działać bez problemów. W razie sugestii lub pytań można udać się do sekcji Issues.

## Komendy bota
**Ogólne**

`//trans <lang> fraza` - przetłumaczenie frazy (język wykrywany automatycznie) na podany

`//ru fraza` - tłumaczenie frazy (język wykrywany automatycznie) na język rosyjski

`//grant <perm> <@użytkownik>` - nadanie uprawnienia dla użytkownika (głosowanie)
- daje uprawnienie kategorii _user_

`//ungrant <perm> <@użytkownik>` - odebranie uprawnienia dla użytkownika (głosowanie)
- próba odebrania uprawnienia kategorii _admin_ skutkuje komunikatem o błędzie

`//perms` - wyświetla permisje autora wiadomości

`//covid` - (beta) wyświetla najnowsze statystyki COVID (źródło: koronawirus.abczdrowie.pl)

`//link` - wysyła link pozwalający botowi dołączyć do serwera

`//pEvent` - (beta) dodaje symbol jakiegoś wydarzenia do avatara (strajk kobiet)

**Dla osób z uprawnieniami**

`//ring` - Dołączenie do kanału autora; włączenie sygnału; opuszczenie kanału

`//volume <volume>` - zmiana głośności bota

`//grant <perm> <@użytkownik>` - nadanie uprawnienia dla użytkownika
- _admin_ daje uprawnienia _admin_
- _user_ daje uprawnienia _user_

`//ungrant <perm> <@użytkownik>` - odebranie uprawnienia dla użytkownika
- _user_ może odebrać tylko uprawnienie _user_ (inaczej błąd)

`//votes <votes>` - zmiana ilości osób niezbędnych do przegłosowania uprawnień

`//rm <"msg"> <s> <l>` - (beta, chwilowo dostępne dla każdego użytkownika) wysyła przypomnienie _msg_ po _s_ sekundach zaczynającego się na _l_

## Ostatnia stabilna wersja - v2.2.0
## Ostatnia wersja beta - v2.4.2-beta
