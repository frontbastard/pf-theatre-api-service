from django.contrib import admin

from theatre.models import (
    TheatreHall,
    Ticket,
    Performance,
    Reservation,
    Genre,
    Actor,
    Play
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(TheatreHall)
admin.site.register(Ticket)
admin.site.register(Performance)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Play)
