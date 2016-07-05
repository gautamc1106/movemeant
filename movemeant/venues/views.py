from django.http import Http404

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from venues.models import Cohort, Region, Venue, VenueCheckin, VenueReveal
from venues.serializers import CohortSerializer, VenueSerializer

from venues.foursquare import search as geo_search


class CohortViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer


class VenueLogAPIHandler(APIView):
    """
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        response = {
            'results': []
        }

        user = request.user
        cohort = request.user.cohort_set.all().first()

        # get all the venuecheckins for the user's cohort
        checkins = VenueCheckin.objects.filter(cohort=cohort)
        for checkin in checkins:
            response['results'].append({
                'foursquare_id': checkin.venue.foursquare_id,
                'name': checkin.venue.name,
                'category': checkin.venue.category,
                'lat': checkin.venue.lat,
                'lng': checkin.venue.lng,

                'checkins': checkin.count,
                'reveals': 0
            })


        return Response(response, status=status.HTTP_200_OK)


class VenueCheckinAPIHandler(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        lat = self.request.data.get('lat', None)
        lng = self.request.data.get('lng', None)

        if lat and lng:
            geo_lookup_results = geo_search(lat, lng)

            if geo_lookup_results:
                print geo_lookup_results

                venue, created = Venue.objects.get_or_create(
                    foursquare_id = geo_lookup_results['foursquare_id']
                )

                venue.name = geo_lookup_results['name']
                venue.category = geo_lookup_results['category']
                venue.lat = geo_lookup_results['lat']
                venue.lng = geo_lookup_results['lng']
                venue.save()

                # log the visit
                checkin, created = VenueCheckin.objects.get_or_create(
                    cohort = request.user.cohort_set.all().first(),
                    venue = venue
                )
                checkin.count = checkin.count + 1;
                checkin.save()

                venue_serializer = VenueSerializer(venue)

                return Response(venue_serializer.data, status=status.HTTP_200_OK)
                
            else:
                # no valid venue found
                return Response(status=status.HTTP_404_NOT_FOUND)

        else:
            # we need lat/lng
            return Response(status=status.HTTP_400_BAD_REQUEST)
