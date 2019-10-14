"""
Removes extra linebreaks from submitted answers
"""
from django.core.management import BaseCommand
from dashboard.models import Answer


class Command(BaseCommand):
    help = "removes extra linebreaks from submitted answers"

    def handle(self, *args, **options):
        answer_1 = Answer.objects.get(pk=1)
        answer_1.answer_text = '<p><span style="background-color: transparent; color: rgb(0, 0, 0);">There may be billions of trillions of planets in the universe, all too far for us to see, but we do know our own solar system, and these planets are definitely round, nearly spherical.&nbsp; How did they get that way?</span></p><p><span style="background-color: transparent; color: rgb(0, 0, 0);">The story began 4.6 billion years ago when a part of a giant molecular cloud got dense enough to begin collapsing inwards by its own gravitational attraction.&nbsp; As it collapsed it spun faster.  Most of its mass collected at the centre, getting hotter due to collisions of the atoms in it.  This part later became the sun, while the outer part flattened into a spinning disc that slowly formed the planets.</span></p><p><span style="background-color: transparent; color: rgb(0, 0, 0);">The sun is made of hydrogen and helium nuclei churning in a pool of electrons.&nbsp; It remains round due to the inward force of gravity, which balances the outward pressure of thermonuclear explosions inside the sun.</span></p><p><span style="background-color: transparent; color: rgb(0, 0, 0);">Unlike the sun, the planets were formed mostly as solids or liquids, out of the relatively cooler disc of dust and gas which surrounded the early sun.&nbsp; Grains of dust collided to form clumps which joined with other clumps and became large enough for gravity to hold them together.  The inner planets, Mercury, Venus, Earth and Mars, got formed when some heavier materials with higher melting points (like iron, nickel, aluminium and rocky silicates) condensed close to the sun.&nbsp; More volatile hydrogen compounds got blown further out where it was cooler and formed the large outer planets, Jupiter, Saturn, Uranus and Neptune.</span></p><p><span style="background-color: transparent; color: rgb(0, 0, 0);">So unlike the sun, planets and their moons were formed mostly as solid or liquid.&nbsp; When atoms and molecules of a solid or liquid are pressed too close there is a repulsive force between them.&nbsp; This force balances the inward attractive force of gravity.  The net result of the symmetrical inward and outward forces is that the planet becomes round in shape.</span></p><p><span style="background-color: transparent; color: rgb(0, 0, 0);">Our Earth may look solid on the surface but deep underground, below about 100 kilometres, the rocks melt under the heat and pressure, and behave like a very viscous liquid.&nbsp; (Scientists believe that nearer the centre there is again a solid core.)  Under sufficient pressure solids deform and “flow” like a liquid, though very slowly, over millions of years.&nbsp; This flow makes it easier for the planet to become round.</span></p><p><span style="background-color: transparent; color: rgb(0, 0, 0);">Knowing that all these round shapes are the effect of gravity, it is easy to see why asteroids are not spherical: they are simply not big enough for gravity to do its work.</span></p><p><span style="background-color: transparent; color: rgb(0, 0, 0);">But gravity has its limits!&nbsp; The rotation of the planets tends to flatten them out.&nbsp; The earth\'s rotation makes it bulge out at the centre and flatten at the poles.&nbsp; Other planets bulge out in the same way.  Going back billions of years the spinning of the protoplanetary mass flattened it to a disc, so now the solar system is flattened.&nbsp; And far far beyond, vast galaxies containing hundred of billions of stars all held together by gravity, are flattened into discs because of their rapidly rotating masses.  How amazing is that!</span></p>'
        answer_1.save()